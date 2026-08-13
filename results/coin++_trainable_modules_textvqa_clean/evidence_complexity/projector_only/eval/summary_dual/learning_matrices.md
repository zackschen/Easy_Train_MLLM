# CoIN++ Evidence Complexity Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.2611 | 0.2518 | 0.2507 | 0.0024 | 0.0139 |
| LLM Judge | 0.2864 | 0.2773 | 0.2867 | 0.0060 | -0.0005 |

## Standard Score Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.2485 | 0.2008 | 0.1441 | 0.2467 |
| multi_evidence | 0.2821 | 0.2389 | 0.1809 | 0.2817 |
| cross_region_or_multihop | 0.2752 | 0.2201 | 0.2166 | 0.2576 |
| cross_context | 0.2866 | 0.2317 | 0.2273 | 0.2986 |

## LLM-Judge Score Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.2872 | 0.2468 | 0.1638 | 0.3180 |
| multi_evidence | 0.2928 | 0.2737 | 0.1943 | 0.3569 |
| cross_region_or_multihop | 0.2858 | 0.2493 | 0.2216 | 0.3297 |
| cross_context | 0.2996 | 0.2557 | 0.2258 | 0.3644 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.2485 | 0.2866 | 0.2866 | 0.0000 | 0.0381 |
| multi_evidence | 0.2389 | 0.2389 | 0.2317 | 0.0073 | -0.0073 |
| cross_region_or_multihop | 0.2166 | 0.2273 | 0.2273 | 0.0000 | 0.0107 |
| cross_context | 0.2986 | 0.2986 | 0.2986 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.2872 | 0.2996 | 0.2996 | 0.0000 | 0.0124 |
| multi_evidence | 0.2737 | 0.2737 | 0.2557 | 0.0180 | -0.0180 |
| cross_region_or_multihop | 0.2216 | 0.2258 | 0.2258 | 0.0000 | 0.0042 |
| cross_context | 0.3644 | 0.3644 | 0.3644 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| single_evidence | single_evidence | 100.0% | 0.0% | 100.0% | 86.7% |
| single_evidence | multi_evidence | 100.0% | 0.0% | 100.0% | 88.4% |
| single_evidence | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 90.6% |
| single_evidence | cross_context | 100.0% | 0.0% | 100.0% | 86.6% |
| multi_evidence | single_evidence | 100.0% | 0.0% | 100.0% | 87.4% |
| multi_evidence | multi_evidence | 100.0% | 0.0% | 100.0% | 89.7% |
| multi_evidence | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 90.7% |
| multi_evidence | cross_context | 100.0% | 0.0% | 100.0% | 88.3% |
| cross_region_or_multihop | single_evidence | 100.0% | 0.0% | 100.0% | 87.6% |
| cross_region_or_multihop | multi_evidence | 100.0% | 0.0% | 100.0% | 89.4% |
| cross_region_or_multihop | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 90.8% |
| cross_region_or_multihop | cross_context | 100.0% | 0.0% | 100.0% | 87.9% |
| cross_context | single_evidence | 100.0% | 0.0% | 100.0% | 87.1% |
| cross_context | multi_evidence | 100.0% | 0.0% | 100.0% | 90.7% |
| cross_context | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 92.5% |
| cross_context | cross_context | 100.0% | 0.0% | 100.0% | 88.4% |
