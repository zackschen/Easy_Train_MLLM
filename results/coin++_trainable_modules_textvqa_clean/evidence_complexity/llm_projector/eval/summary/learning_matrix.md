# Factor-1 Evidence Complexity Continual Evaluation (relaxed_match)

## Performance Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.391 | 0.297 | 0.213 | 0.347 |
| multi_evidence | 0.370 | 0.350 | 0.201 | 0.348 |
| cross_region_or_multihop | 0.331 | 0.303 | 0.324 | 0.342 |
| cross_context | 0.323 | 0.332 | 0.300 | 0.441 |

## Forgetting

| Task | Score at learning | Best after learning | Final score | Forgetting |
|---|---:|---:|---:|---:|
| single_evidence | 0.391000 | 0.391000 | 0.323000 | 0.068000 |
| multi_evidence | 0.350000 | 0.350000 | 0.332000 | 0.018000 |
| cross_region_or_multihop | 0.324000 | 0.324000 | 0.300000 | 0.024000 |
| cross_context | 0.441000 | 0.441000 | 0.441000 | 0.000000 |
