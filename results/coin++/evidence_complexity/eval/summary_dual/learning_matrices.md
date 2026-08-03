# CoIN++ Evidence Complexity Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.2448 | 0.2683 | 0.3024 | 0.0767 | -0.0767 |
| LLM Judge | 0.2576 | 0.2767 | 0.3158 | 0.0776 | -0.0776 |

## Standard Score Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.4035 | 0.2831 | 0.2073 | 0.3533 |
| multi_evidence | 0.2121 | 0.2436 | 0.1505 | 0.2887 |
| cross_region_or_multihop | 0.2041 | 0.1827 | 0.2044 | 0.2434 |
| cross_context | 0.2208 | 0.2154 | 0.1853 | 0.3580 |

## LLM-Judge Score Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.4175 | 0.3009 | 0.1933 | 0.4002 |
| multi_evidence | 0.2102 | 0.2529 | 0.1399 | 0.3228 |
| cross_region_or_multihop | 0.1993 | 0.1959 | 0.2047 | 0.2808 |
| cross_context | 0.2240 | 0.2329 | 0.1854 | 0.3883 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.4035 | 0.4035 | 0.2208 | 0.1827 | -0.1827 |
| multi_evidence | 0.2436 | 0.2436 | 0.2154 | 0.0282 | -0.0282 |
| cross_region_or_multihop | 0.2044 | 0.2044 | 0.1853 | 0.0192 | -0.0192 |
| cross_context | 0.3580 | 0.3580 | 0.3580 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.4175 | 0.4175 | 0.2240 | 0.1935 | -0.1935 |
| multi_evidence | 0.2529 | 0.2529 | 0.2329 | 0.0200 | -0.0200 |
| cross_region_or_multihop | 0.2047 | 0.2047 | 0.1854 | 0.0193 | -0.0193 |
| cross_context | 0.3883 | 0.3883 | 0.3883 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| single_evidence | single_evidence | 100.0% | 0.0% | 100.0% | 90.7% |
| single_evidence | multi_evidence | 100.0% | 0.0% | 100.0% | 90.8% |
| single_evidence | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 92.6% |
| single_evidence | cross_context | 100.0% | 0.0% | 100.0% | 89.9% |
| multi_evidence | single_evidence | 100.0% | 0.0% | 100.0% | 95.1% |
| multi_evidence | multi_evidence | 100.0% | 0.0% | 100.0% | 94.0% |
| multi_evidence | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 93.7% |
| multi_evidence | cross_context | 100.0% | 0.0% | 100.0% | 90.6% |
| cross_region_or_multihop | single_evidence | 100.0% | 0.0% | 100.0% | 94.3% |
| cross_region_or_multihop | multi_evidence | 100.0% | 0.0% | 100.0% | 93.1% |
| cross_region_or_multihop | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 94.2% |
| cross_region_or_multihop | cross_context | 100.0% | 0.0% | 100.0% | 91.6% |
| cross_context | single_evidence | 100.0% | 0.0% | 100.0% | 92.9% |
| cross_context | multi_evidence | 100.0% | 0.0% | 100.0% | 92.4% |
| cross_context | cross_region_or_multihop | 100.0% | 0.0% | 100.0% | 94.8% |
| cross_context | cross_context | 100.0% | 0.0% | 100.0% | 92.5% |
