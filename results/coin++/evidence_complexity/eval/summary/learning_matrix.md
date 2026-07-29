# Factor-1 Evidence Continual Evaluation (relaxed_match)

## Performance Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.373 | 0.283 | 0.217 | 0.345 |
| multi_evidence | 0.209 | 0.261 | 0.160 | 0.278 |
| cross_region_or_multihop | 0.237 | 0.236 | 0.248 | 0.311 |
| cross_context | 0.228 | 0.244 | 0.217 | 0.372 |

## Forgetting

| Task | Score at learning | Best after learning | Final score | Forgetting |
|---|---:|---:|---:|---:|
| single_evidence | 0.373000 | 0.373000 | 0.228000 | 0.145000 |
| multi_evidence | 0.261000 | 0.261000 | 0.244000 | 0.017000 |
| cross_region_or_multihop | 0.248000 | 0.248000 | 0.217000 | 0.031000 |
| cross_context | 0.372000 | 0.372000 | 0.372000 | 0.000000 |
