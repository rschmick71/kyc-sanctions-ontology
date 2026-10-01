# ADR-0003 — Graph for facts and policy, code for arithmetic

- **Status:** Accepted
- **Date:** 2026-09-29

## Context

UBO identification requires **look-through ownership**: if Omar owns 100% of
Tidewater, and Tidewater owns 25% of Harbourline, Omar effectively owns 25%
of Harbourline.

SPARQL property paths (`kso:heldIn+`) can *follow* chains of any length but
cannot *multiply* values along them. Workarounds (a UNION per chain depth)
hard-code a maximum depth and silently miss deeper structures, which are
exactly the ones layered to obscure ownership.

## Decision

- The graph holds **facts** (stakes) and **policy** (thresholds on FATF-status
  concepts in `vocabularies/`).
- A small Python function (`kso.ownership.effective_ownership`) does the
  recursive multiply-and-sum, with a cycle guard for circular structures.
- The threshold is **read from the graph**, never hard-coded in Python, so a
  policy change is a data change.

## Consequences

- SPARQL competency queries stay declarative and readable. CQ1 deliberately
  covers only direct stakes and says so.
- The result can be written back as `kso:BeneficialOwnerDetermination` nodes,
  so downstream queries see computed UBOs as ordinary graph facts.
- This is the neuro-symbolic seam in miniature: the symbolic layer holds
  meaning and rules, procedural code does what the logic layer can't. An LLM
  or agent would sit on this seam the same way, reading from and writing
  determinations back to the graph under SHACL validation.
