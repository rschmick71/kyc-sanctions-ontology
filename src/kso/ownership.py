"""Effective (look-through) beneficial ownership.

Why this lives in Python and not SPARQL: a SPARQL property path such as
`kso:heldIn+` can *follow* an ownership chain of any length, but it cannot
*multiply* the percentages along the way. 100% of an entity that owns 25%
is an effective 25% — that arithmetic needs a small recursive walk.

This is the "hybrid" pattern in miniature: the graph holds the facts and the
policy (thresholds), and code does the one thing the query language can't.
"""

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from rdflib import RDF, Graph, URIRef

from kso.graph import KSO

HUNDRED = Decimal(100)


@dataclass(frozen=True)
class BeneficialOwner:
    person: URIRef
    name: str
    effective_percent: Decimal


def direct_stakes(graph: Graph, entity: URIRef) -> list[tuple[URIRef, Decimal]]:
    """(holder, percent) for every stake held directly in `entity`."""
    stakes = []
    for stake in graph.subjects(KSO.heldIn, entity):
        holder = graph.value(stake, KSO.holder)
        percent = Decimal(str(graph.value(stake, KSO.percentage)))
        stakes.append((holder, percent))
    return stakes


def effective_ownership(graph: Graph, entity: URIRef) -> dict[URIRef, Decimal]:
    """Each natural person's look-through percentage of `entity`.

    Stakes are multiplied down every chain and summed across chains, so a
    person who owns through two different holding companies gets both.
    """
    totals: dict[URIRef, Decimal] = defaultdict(Decimal)

    def walk(current: URIRef, share: Decimal, visited: frozenset[URIRef]) -> None:
        for holder, percent in direct_stakes(graph, current):
            holder_share = share * percent / HUNDRED
            if (holder, RDF.type, KSO.NaturalPerson) in graph:
                totals[holder] += holder_share
            elif holder not in visited:  # circular ownership guard
                walk(holder, holder_share, visited | {holder})

    walk(entity, HUNDRED, frozenset({entity}))
    return dict(totals)


def ubo_threshold(graph: Graph, entity: URIRef) -> Decimal:
    """Threshold implied by the FATF status of the entity's incorporation jurisdiction."""
    jurisdiction = graph.value(entity, KSO.incorporatedIn)
    status = graph.value(jurisdiction, KSO.hasFatfStatus)
    threshold = graph.value(status, KSO.uboThresholdPercent)
    if threshold is None:
        raise ValueError(f"No UBO threshold resolvable for {entity}")
    return Decimal(str(threshold))


def reportable_owners(
    graph: Graph, entity: URIRef, threshold: Decimal | None = None
) -> list[BeneficialOwner]:
    """Natural persons at or above the threshold, largest stake first."""
    cutoff = ubo_threshold(graph, entity) if threshold is None else threshold
    owners = [
        BeneficialOwner(person, str(graph.value(person, KSO.legalName)), percent)
        for person, percent in effective_ownership(graph, entity).items()
        if percent >= cutoff
    ]
    return sorted(owners, key=lambda owner: owner.effective_percent, reverse=True)
