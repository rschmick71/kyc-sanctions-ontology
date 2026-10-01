# ADR-0002 — SHACL for validation, OWL for meaning

- **Status:** Accepted
- **Date:** 2026-09-29

## Context

A common mistake is to use OWL to *enforce* data rules. For example, writing
`kso:heldIn rdfs:range kso:LegalEntity` and expecting an error when someone
points a stake at a person.

OWL doesn't work that way. It runs under the **open-world assumption**: a
missing fact is *unknown*, not *false*, and a range axiom is a license to
*infer*. Point a stake at `ex:Alice` and an OWL reasoner will quietly conclude
that Alice is a LegalEntity. If Alice is also declared a NaturalPerson, the
reasoner finds an inconsistency across the *whole* graph, and nothing tells
you which record is wrong.

KYC is a **closed-world** problem. "We do not hold the UBO's photo ID" is a
finding that blocks onboarding, not an unknown.

## Decision

- **OWL** (`ontology/`) states what terms *mean*: classes, properties,
  disjointness, functional and transitive characteristics.
- **SHACL** (`shapes/`) states what a *valid record* must contain: cardinalities,
  datatypes, value lists, patterns, and cross-node policy rules written as
  SHACL-SPARQL (stakes ≤ 100%, maker ≠ checker, an escalated case must be locked).
- Validation runs with RDFS inference only, so subclass typing works
  (a ForeignExtension counts as a CustomerProfile) without OWL's
  inference surprises.

## Consequences

- Violations are reported **per focus node with a human message**, the
  format a 1LOD ops analyst can actually act on.
- Policy changes (e.g. a new mandatory field) are shape edits, not ontology
  changes, so the model stays stable while the rules evolve.
- Two artefacts to keep in sync. The test suite makes sure the bundled
  example conforms and that each key policy rule rejects a bad record.
