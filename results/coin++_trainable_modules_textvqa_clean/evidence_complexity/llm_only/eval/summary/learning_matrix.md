# Factor-1 Evidence Complexity Continual Evaluation (relaxed_match)

## Performance Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.404 | 0.300 | 0.221 | 0.349 |
| multi_evidence | 0.381 | 0.364 | 0.209 | 0.333 |
| cross_region_or_multihop | 0.323 | 0.304 | 0.306 | 0.343 |
| cross_context | 0.340 | 0.325 | 0.311 | 0.430 |

## Forgetting

| Task | Score at learning | Best after learning | Final score | Forgetting |
|---|---:|---:|---:|---:|
| single_evidence | 0.404000 | 0.404000 | 0.340000 | 0.064000 |
| multi_evidence | 0.364000 | 0.364000 | 0.325000 | 0.039000 |
| cross_region_or_multihop | 0.306000 | 0.311000 | 0.311000 | 0.000000 |
| cross_context | 0.430000 | 0.430000 | 0.430000 | 0.000000 |
