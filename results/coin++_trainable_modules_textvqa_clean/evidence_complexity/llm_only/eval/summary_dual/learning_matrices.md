# CoIN++ Evidence Complexity Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.3553 | 0.3713 | 0.3817 | 0.0352 | -0.0352 |
| LLM Judge | 0.3755 | 0.3819 | 0.4012 | 0.0343 | -0.0343 |

## Standard Score Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.4381 | 0.2847 | 0.1955 | 0.3521 |
| multi_evidence | 0.4157 | 0.3598 | 0.1984 | 0.3430 |
| cross_region_or_multihop | 0.3354 | 0.2805 | 0.2961 | 0.3303 |
| cross_context | 0.3637 | 0.3287 | 0.2961 | 0.4328 |

## LLM-Judge Score Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.4396 | 0.3203 | 0.1898 | 0.4105 |
| multi_evidence | 0.4035 | 0.3809 | 0.1988 | 0.3809 |
| cross_region_or_multihop | 0.3427 | 0.3090 | 0.3094 | 0.3780 |
| cross_context | 0.3754 | 0.3474 | 0.3043 | 0.4747 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.4381 | 0.4381 | 0.3637 | 0.0745 | -0.0745 |
| multi_evidence | 0.3598 | 0.3598 | 0.3287 | 0.0311 | -0.0311 |
| cross_region_or_multihop | 0.2961 | 0.2961 | 0.2961 | 0.0000 | 0.0001 |
| cross_context | 0.4328 | 0.4328 | 0.4328 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.4396 | 0.4396 | 0.3754 | 0.0642 | -0.0642 |
| multi_evidence | 0.3809 | 0.3809 | 0.3474 | 0.0335 | -0.0335 |
| cross_region_or_multihop | 0.3094 | 0.3094 | 0.3043 | 0.0051 | -0.0051 |
| cross_context | 0.4747 | 0.4747 | 0.4747 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| single_evidence | single_evidence | 100.0% | 0.0% | 100.0% | 88.9% |
| single_evidence | multi_evidence | 100.0% | 0.0% | 100.0% | 90.4% |
| single_evidence | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 92.2% |
| single_evidence | cross_context | 100.0% | 0.0% | 100.0% | 88.6% |
| multi_evidence | single_evidence | 100.0% | 0.0% | 100.0% | 89.4% |
| multi_evidence | multi_evidence | 100.0% | 0.0% | 100.0% | 91.0% |
| multi_evidence | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 92.8% |
| multi_evidence | cross_context | 100.0% | 0.0% | 100.0% | 90.3% |
| cross_region_or_multihop | single_evidence | 100.0% | 0.0% | 100.0% | 90.4% |
| cross_region_or_multihop | multi_evidence | 100.0% | 0.0% | 100.0% | 90.1% |
| cross_region_or_multihop | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 92.0% |
| cross_region_or_multihop | cross_context | 100.0% | 0.0% | 100.0% | 91.3% |
| cross_context | single_evidence | 100.0% | 0.0% | 100.0% | 90.0% |
| cross_context | multi_evidence | 100.0% | 0.0% | 100.0% | 91.5% |
| cross_context | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 93.3% |
| cross_context | cross_context | 100.0% | 0.0% | 100.0% | 91.6% |
