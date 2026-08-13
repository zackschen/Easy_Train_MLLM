# CoIN++ Evidence Complexity Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.3522 | 0.3672 | 0.3834 | 0.0415 | -0.0415 |
| LLM Judge | 0.3716 | 0.3756 | 0.3969 | 0.0337 | -0.0337 |

## Standard Score Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.4268 | 0.2981 | 0.1927 | 0.3562 |
| multi_evidence | 0.4086 | 0.3502 | 0.1940 | 0.3488 |
| cross_region_or_multihop | 0.3462 | 0.2759 | 0.3089 | 0.3317 |
| cross_context | 0.3583 | 0.3210 | 0.2820 | 0.4476 |

## LLM-Judge Score Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.4232 | 0.3283 | 0.1885 | 0.4114 |
| multi_evidence | 0.4050 | 0.3669 | 0.1959 | 0.3961 |
| cross_region_or_multihop | 0.3448 | 0.3064 | 0.3143 | 0.3816 |
| cross_context | 0.3643 | 0.3491 | 0.2899 | 0.4831 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.4268 | 0.4268 | 0.3583 | 0.0685 | -0.0685 |
| multi_evidence | 0.3502 | 0.3502 | 0.3210 | 0.0292 | -0.0292 |
| cross_region_or_multihop | 0.3089 | 0.3089 | 0.2820 | 0.0269 | -0.0269 |
| cross_context | 0.4476 | 0.4476 | 0.4476 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.4232 | 0.4232 | 0.3643 | 0.0589 | -0.0589 |
| multi_evidence | 0.3669 | 0.3669 | 0.3491 | 0.0178 | -0.0178 |
| cross_region_or_multihop | 0.3143 | 0.3143 | 0.2899 | 0.0244 | -0.0244 |
| cross_context | 0.4831 | 0.4831 | 0.4831 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| single_evidence | single_evidence | 100.0% | 0.0% | 100.0% | 89.7% |
| single_evidence | multi_evidence | 100.0% | 0.0% | 100.0% | 90.8% |
| single_evidence | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 91.5% |
| single_evidence | cross_context | 100.0% | 0.0% | 100.0% | 89.6% |
| multi_evidence | single_evidence | 100.0% | 0.0% | 100.0% | 89.3% |
| multi_evidence | multi_evidence | 100.0% | 0.0% | 100.0% | 91.3% |
| multi_evidence | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 92.3% |
| multi_evidence | cross_context | 100.0% | 0.0% | 100.0% | 89.8% |
| cross_region_or_multihop | single_evidence | 100.0% | 0.0% | 100.0% | 89.7% |
| cross_region_or_multihop | multi_evidence | 100.0% | 0.0% | 100.0% | 89.9% |
| cross_region_or_multihop | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 92.4% |
| cross_region_or_multihop | cross_context | 100.0% | 0.0% | 100.0% | 90.5% |
| cross_context | single_evidence | 100.0% | 0.0% | 100.0% | 89.7% |
| cross_context | multi_evidence | 100.0% | 0.0% | 100.0% | 91.2% |
| cross_context | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 93.1% |
| cross_context | cross_context | 100.0% | 0.0% | 100.0% | 91.7% |
