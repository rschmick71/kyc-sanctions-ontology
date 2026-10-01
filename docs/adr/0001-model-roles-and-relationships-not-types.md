# ADR-0001 — Model roles and relationships, not types

- **Status:** Accepted
- **Date:** 2026-09-29

## Context

The obvious first model of KYC is a class hierarchy: `Customer`, `UBO`,
`Director`, `Respondent`, each a subclass of `Person` or `Company`. It reads
well and breaks almost immediately:

- The same person is a UBO of one entity, a director of another, and a
  customer in their own right. Multiple inheritance explodes.
- "UBO" is not a property of a person. It is the *outcome of a calculation*
  over a specific entity, at a specific threshold, on a specific date. At 25%
  a 12% shareholder is not a UBO; after a FATF grey-listing drops the
  threshold to 10%, the same person with the same shares is one.
- An ownership percentage belongs to the *relationship*, not to either end.
  A plain triple `:Alice :owns :AcmeLtd` has nowhere to put "55%".

## Decision

1. Keep only a small set of **rigid types** — things that are what they are
   regardless of context: `NaturalPerson`, `LegalEntity`, `FinancialInstitution`,
   `Jurisdiction`, `Vessel`, `Goods`.
2. **Reify relationships that carry data** as classes:
   `OwnershipStake` (holder, heldIn, percentage), `ControlRelationship`,
   `CorrespondentRelationship`.
3. Record **UBO status as a determination**, `BeneficialOwnerDetermination`,
   linking person, entity, effective percentage and the threshold applied.
4. Model the customer relationship as a **profile** (`MasterProfile`,
   `ForeignExtension`) that points at a party, rather than making "customer"
   a kind of party.

## Consequences

- Queries are slightly longer (one extra hop through the stake node).
- Every historical determination is auditable: you can show an examiner
  exactly which threshold produced which UBO list and when.
- Follows the same reified-shareholding pattern as the EDM Council's FIBO,
  which keeps a future alignment (`skos:closeMatch` mappings) cheap.
