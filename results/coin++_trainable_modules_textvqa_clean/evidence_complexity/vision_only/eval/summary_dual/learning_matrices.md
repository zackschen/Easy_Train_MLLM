# CoIN++ Evidence Complexity Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.1657 | 0.1089 | 0.1117 | 0.0000 | 0.0721 |
| LLM Judge | 0.2491 | 0.2447 | 0.2397 | 0.0026 | 0.0125 |

## Standard Score Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.0729 | 0.0498 | 0.0485 | 0.0546 |
| multi_evidence | 0.0874 | 0.0785 | 0.0726 | 0.0864 |
| cross_region_or_multihop | 0.1230 | 0.1068 | 0.1128 | 0.1178 |
| cross_context | 0.1827 | 0.1566 | 0.1411 | 0.1826 |

## LLM-Judge Score Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.2438 | 0.2009 | 0.1313 | 0.2517 |
| multi_evidence | 0.2724 | 0.2317 | 0.1516 | 0.2840 |
| cross_region_or_multihop | 0.2689 | 0.2483 | 0.1837 | 0.2976 |
| cross_context | 0.2688 | 0.2451 | 0.1828 | 0.2998 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.0729 | 0.1827 | 0.1827 | 0.0000 | 0.1098 |
| multi_evidence | 0.0785 | 0.1566 | 0.1566 | 0.0000 | 0.0782 |
| cross_region_or_multihop | 0.1128 | 0.1411 | 0.1411 | 0.0000 | 0.0283 |
| cross_context | 0.1826 | 0.1826 | 0.1826 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.2438 | 0.2724 | 0.2688 | 0.0036 | 0.0250 |
| multi_evidence | 0.2317 | 0.2483 | 0.2451 | 0.0032 | 0.0134 |
| cross_region_or_multihop | 0.1837 | 0.1837 | 0.1828 | 0.0009 | -0.0009 |
| cross_context | 0.2998 | 0.2998 | 0.2998 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| single_evidence | single_evidence | 100.0% | 0.0% | 100.0% | 76.7% |
| single_evidence | multi_evidence | 100.0% | 0.0% | 100.0% | 81.2% |
| single_evidence | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 86.7% |
| single_evidence | cross_context | 100.0% | 0.0% | 100.0% | 77.3% |
| multi_evidence | single_evidence | 100.0% | 0.0% | 100.0% | 75.9% |
| multi_evidence | multi_evidence | 100.0% | 0.0% | 100.0% | 81.6% |
| multi_evidence | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 86.2% |
| multi_evidence | cross_context | 100.0% | 0.0% | 100.0% | 75.3% |
| cross_region_or_multihop | single_evidence | 100.0% | 0.0% | 100.0% | 77.4% |
| cross_region_or_multihop | multi_evidence | 100.0% | 0.0% | 100.0% | 81.9% |
| cross_region_or_multihop | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 86.8% |
| cross_region_or_multihop | cross_context | 100.0% | 0.0% | 100.0% | 76.7% |
| cross_context | single_evidence | 100.0% | 0.0% | 100.0% | 83.3% |
| cross_context | multi_evidence | 100.0% | 0.0% | 100.0% | 87.1% |
| cross_context | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 89.7% |
| cross_context | cross_context | 100.0% | 0.0% | 100.0% | 81.6% |
