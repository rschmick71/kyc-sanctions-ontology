# ADR-0004 — Reference data as SKOS vocabularies, separate from the ontology

- **Status:** Accepted
- **Date:** 2026-09-29

## Context

FATF statuses change after every plenary (February, June, October). Risk
tiers and local document requirements change on regulator timelines. The
class model (what a jurisdiction *is*) changes rarely.

Hard-coding reference values as OWL classes (`class HighRisk`) or mixing them
into the ontology files couples a slow-moving model to fast-moving data, and
makes every status change look like a schema change in version control.

## Decision

- Controlled values (case states, risk tiers, FATF statuses, escalation
  triggers, document types) are **SKOS concepts** in `vocabularies/`.
- Jurisdictions are instances of both `kso:Jurisdiction` and `skos:Concept`.
- **The UBO threshold is attached once, to the FATF-status concept**, not
  copied onto each of the 20 jurisdictions. One fact, one place.
- `jurisdictions.ttl` carries `dcterms:modified` and a scope note requiring
  re-verification each FATF plenary.

## Consequences

- A grey-list change is a one-line diff (`kso:hasFatfStatus`) that is easy to
  review, date and audit.
- The ontology version and the reference-data version can move independently.
