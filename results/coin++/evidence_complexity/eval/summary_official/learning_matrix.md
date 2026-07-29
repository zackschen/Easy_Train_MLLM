# CoIN++ Evidence Complexity Evaluation

Primary metric: `primary_score`. Final average: **0.2448**; average forgetting on old tasks: **0.0767**; BWT: **-0.0767**.

## Continual Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.4035 | 0.2831 | 0.2073 | 0.3533 |
| multi_evidence | 0.2121 | 0.2436 | 0.1505 | 0.2887 |
| cross_region_or_multihop | 0.2041 | 0.1827 | 0.2044 | 0.2434 |
| cross_context | 0.2208 | 0.2154 | 0.1853 | 0.3580 |

## Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| single_evidence | 0.4035 | 0.4035 | 0.2208 | 0.1827 | -0.1827 |
| multi_evidence | 0.2436 | 0.2436 | 0.2154 | 0.0282 | -0.0282 |
| cross_region_or_multihop | 0.2044 | 0.2044 | 0.1853 | 0.0192 | -0.0192 |
| cross_context | 0.3580 | 0.3580 | 0.3580 | 0.0000 | 0.0000 |

## Scoring Coverage

| Trained until | Task | Official metric | LLM judge |
|---|---|---:|---:|
| single_evidence | single_evidence | 100.0% | 0.0% |
| single_evidence | multi_evidence | 100.0% | 0.0% |
| single_evidence | cross_region_or_multihop | 100.0% | 0.0% |
| single_evidence | cross_context | 100.0% | 0.0% |
| multi_evidence | single_evidence | 100.0% | 0.0% |
| multi_evidence | multi_evidence | 100.0% | 0.0% |
| multi_evidence | cross_region_or_multihop | 100.0% | 0.0% |
| multi_evidence | cross_context | 100.0% | 0.0% |
| cross_region_or_multihop | single_evidence | 100.0% | 0.0% |
| cross_region_or_multihop | multi_evidence | 100.0% | 0.0% |
| cross_region_or_multihop | cross_region_or_multihop | 100.0% | 0.0% |
| cross_region_or_multihop | cross_context | 100.0% | 0.0% |
| cross_context | single_evidence | 100.0% | 0.0% |
| cross_context | multi_evidence | 100.0% | 0.0% |
| cross_context | cross_region_or_multihop | 100.0% | 0.0% |
| cross_context | cross_context | 100.0% | 0.0% |
