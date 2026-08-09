# Factor-1 Evidence Complexity Continual Evaluation (relaxed_match)

## Performance Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.223 | 0.213 | 0.158 | 0.270 |
| multi_evidence | 0.233 | 0.226 | 0.183 | 0.294 |
| cross_region_or_multihop | 0.230 | 0.224 | 0.207 | 0.270 |
| cross_context | 0.282 | 0.260 | 0.237 | 0.330 |

## Forgetting

| Task | Score at learning | Best after learning | Final score | Forgetting |
|---|---:|---:|---:|---:|
| single_evidence | 0.223000 | 0.282000 | 0.282000 | 0.000000 |
| multi_evidence | 0.226000 | 0.260000 | 0.260000 | 0.000000 |
| cross_region_or_multihop | 0.207000 | 0.237000 | 0.237000 | 0.000000 |
| cross_context | 0.330000 | 0.330000 | 0.330000 | 0.000000 |
