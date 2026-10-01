"""Look-through ownership and the competency queries return the expected answers."""

from decimal import Decimal

import pytest
from rdflib import Graph

from kso.graph import EX, QUERIES_DIR, load_knowledge_graph
from kso.ownership import effective_ownership, reportable_owners, ubo_threshold


@pytest.fixture(scope="module")
def graph() -> Graph:
    return load_knowledge_graph()


def run(graph: Graph, query_prefix: str) -> list[tuple]:
    query_path = next(QUERIES_DIR.glob(f"{query_prefix}*.rq"))
    return [tuple(str(value) for value in row) for row in graph.query(query_path.read_text())]


# --- ownership ---------------------------------------------------------------

def test_indirect_stake_is_multiplied_through_holding_company(graph):
    stakes = effective_ownership(graph, EX.Harbourline)
    assert stakes[EX.OmarHaddad] == Decimal(25)


def test_kenya_nexus_compresses_threshold_to_ten_percent(graph):
    assert ubo_threshold(graph, EX.Harbourline) == Decimal(10)


def test_reportable_owners_at_ten_percent(graph):
    names = [owner.name for owner in reportable_owners(graph, EX.Harbourline)]
    assert names == ["Amara Njoroge", "Omar Haddad", "Daniel Otieno"]


def test_standard_threshold_would_miss_the_twelve_percent_holder(graph):
    names = {owner.name for owner in reportable_owners(graph, EX.Harbourline, Decimal(25))}
    assert "Daniel Otieno" not in names


def test_circular_ownership_terminates():
    turtle = """
        @prefix kso: <https://w3id.org/kso/ontology#> .
        @prefix ex:  <https://w3id.org/kso/example/> .
        ex:A a kso:LegalEntity . ex:B a kso:LegalEntity .
        ex:P a kso:NaturalPerson ; kso:legalName "P" .
        ex:s1 kso:holder ex:B ; kso:heldIn ex:A ; kso:percentage 50.0 .
        ex:s2 kso:holder ex:A ; kso:heldIn ex:B ; kso:percentage 50.0 .
        ex:s3 kso:holder ex:P ; kso:heldIn ex:B ; kso:percentage 50.0 .
    """
    loop = Graph().parse(data=turtle, format="turtle")
    assert effective_ownership(loop, EX.A) == {EX.P: Decimal(25)}


# --- competency queries -------------------------------------------------------

def test_cq01_direct_owners_above_threshold(graph):
    rows = run(graph, "cq01")
    harbourline = [person for entity, person, *_ in rows if entity == "Harbourline Commodities Ltd"]
    assert harbourline == ["Amara Njoroge", "Daniel Otieno"]  # Haddad is only indirect here
    assert ("Tidewater Holdings FZE", "Omar Haddad") in {(row[0], row[1]) for row in rows}


def test_cq02_edd_has_both_reasons(graph):
    reasons = {row[2] for row in run(graph, "cq02")}
    assert any(reason.startswith("FATF nexus: Kenya") for reason in reasons)
    assert any("Risk assessment" in reason for reason in reasons)


def test_cq03_finds_the_missing_singapore_document(graph):
    missing = [row[2] for row in run(graph, "cq03")]
    assert missing == ["Local Resident Director Verification"]


def test_cq04_lists_the_locked_escalation(graph):
    rows = run(graph, "cq04")
    assert len(rows) == 1
    assert rows[0][1] == "Harbourline Commodities Ltd"


def test_cq05_flags_kenya_and_vietnam_legs(graph):
    exposures = {row[2] for row in run(graph, "cq05")}
    assert exposures == {"Route touches Kenya", "Route touches Vietnam"}
