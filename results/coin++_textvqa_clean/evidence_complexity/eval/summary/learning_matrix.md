# Factor-1 Evidence Complexity Continual Evaluation (relaxed_match)

## Performance Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.390 | 0.296 | 0.217 | 0.352 |
| multi_evidence | 0.364 | 0.353 | 0.218 | 0.337 |
| cross_region_or_multihop | 0.318 | 0.305 | 0.319 | 0.339 |
| cross_context | 0.311 | 0.337 | 0.294 | 0.443 |

## Forgetting

| Task | Score at learning | Best after learning | Final score | Forgetting |
|---|---:|---:|---:|---:|
| single_evidence | 0.390000 | 0.390000 | 0.311000 | 0.079000 |
| multi_evidence | 0.353000 | 0.353000 | 0.337000 | 0.016000 |
| cross_region_or_multihop | 0.319000 | 0.319000 | 0.294000 | 0.025000 |
| cross_context | 0.443000 | 0.443000 | 0.443000 | 0.000000 |
