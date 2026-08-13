# CoIN++ Evidence Complexity Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.3518 | 0.3676 | 0.3878 | 0.0480 | -0.0480 |
| LLM Judge | 0.3683 | 0.3748 | 0.3999 | 0.0422 | -0.0422 |

## Standard Score Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.4343 | 0.2924 | 0.1909 | 0.3584 |
| multi_evidence | 0.3961 | 0.3519 | 0.2114 | 0.3431 |
| cross_region_or_multihop | 0.3358 | 0.2838 | 0.3111 | 0.3343 |
| cross_context | 0.3348 | 0.3306 | 0.2880 | 0.4539 |

## LLM-Judge Score Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.4299 | 0.3233 | 0.1862 | 0.4114 |
| multi_evidence | 0.3917 | 0.3711 | 0.2001 | 0.3863 |
| cross_region_or_multihop | 0.3349 | 0.3117 | 0.3123 | 0.3839 |
| cross_context | 0.3438 | 0.3506 | 0.2924 | 0.4864 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.4343 | 0.4343 | 0.3348 | 0.0995 | -0.0995 |
| multi_evidence | 0.3519 | 0.3519 | 0.3306 | 0.0213 | -0.0213 |
| cross_region_or_multihop | 0.3111 | 0.3111 | 0.2880 | 0.0231 | -0.0231 |
| cross_context | 0.4539 | 0.4539 | 0.4539 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.4299 | 0.4299 | 0.3438 | 0.0861 | -0.0861 |
| multi_evidence | 0.3711 | 0.3711 | 0.3506 | 0.0205 | -0.0205 |
| cross_region_or_multihop | 0.3123 | 0.3123 | 0.2924 | 0.0199 | -0.0199 |
| cross_context | 0.4864 | 0.4864 | 0.4864 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| single_evidence | single_evidence | 100.0% | 0.0% | 100.0% | 89.4% |
| single_evidence | multi_evidence | 100.0% | 0.0% | 100.0% | 90.8% |
| single_evidence | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 92.2% |
| single_evidence | cross_context | 100.0% | 0.0% | 100.0% | 89.4% |
| multi_evidence | single_evidence | 100.0% | 0.0% | 100.0% | 89.7% |
| multi_evidence | multi_evidence | 100.0% | 0.0% | 100.0% | 91.2% |
| multi_evidence | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 91.9% |
| multi_evidence | cross_context | 100.0% | 0.0% | 100.0% | 89.7% |
| cross_region_or_multihop | single_evidence | 100.0% | 0.0% | 100.0% | 91.9% |
| cross_region_or_multihop | multi_evidence | 100.0% | 0.0% | 100.0% | 90.5% |
| cross_region_or_multihop | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 92.0% |
| cross_region_or_multihop | cross_context | 100.0% | 0.0% | 100.0% | 90.5% |
| cross_context | single_evidence | 100.0% | 0.0% | 100.0% | 90.4% |
| cross_context | multi_evidence | 100.0% | 0.0% | 100.0% | 90.7% |
| cross_context | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 93.2% |
| cross_context | cross_context | 100.0% | 0.0% | 100.0% | 92.1% |
