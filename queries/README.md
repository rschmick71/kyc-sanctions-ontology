# Competency questions

An ontology is only as good as the questions it can answer. Each file here is
one **competency question** (CQ): a real 1LOD question, written as SPARQL, with
a test in `tests/` pinning the expected answer on the bundled example.

| ID | Question | Operating-model step |
|----|----------|----------------------|
| [CQ1](cq01-direct-owners-above-threshold.rq) | Which natural persons directly hold a stake at or above the applicable UBO threshold? | Dynamic UBO traversal |
| [CQ2](cq02-edd-triggers.rq) | Which master profiles require EDD, and why? | Screening & EDD |
| [CQ3](cq03-local-document-gaps.rq) | Which locally required documents are still missing for each foreign extension? | Foreign gap assessment → RFI |
| [CQ4](cq04-locked-escalations.rq) | Which cases are locked awaiting 2LOD, with maker, checker and trigger? | 1LOD → 2LOD escalation |
| [CQ5](cq05-trade-route-exposure.rq) | Which trade transactions route through an EDD jurisdiction or carry dual-use goods? | Trade-finance screening |

Run any of them:

```bash
kso query cq03
```

Look-through (indirect) ownership is intentionally **not** a SPARQL query. See
[ADR-0003](../docs/adr/0003-graph-for-facts-code-for-arithmetic.md) and `kso ubo`.
