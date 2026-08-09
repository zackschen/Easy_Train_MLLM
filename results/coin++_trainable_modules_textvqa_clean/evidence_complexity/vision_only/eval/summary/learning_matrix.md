# Factor-1 Evidence Complexity Continual Evaluation (relaxed_match)

## Performance Matrix

| Trained until | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| single_evidence | 0.203 | 0.186 | 0.143 | 0.239 |
| multi_evidence | 0.206 | 0.198 | 0.146 | 0.262 |
| cross_region_or_multihop | 0.210 | 0.209 | 0.177 | 0.267 |
| cross_context | 0.222 | 0.221 | 0.181 | 0.267 |

## Forgetting

| Task | Score at learning | Best after learning | Final score | Forgetting |
|---|---:|---:|---:|---:|
| single_evidence | 0.203000 | 0.222000 | 0.222000 | 0.000000 |
| multi_evidence | 0.198000 | 0.221000 | 0.221000 | 0.000000 |
| cross_region_or_multihop | 0.177000 | 0.181000 | 0.181000 | 0.000000 |
| cross_context | 0.267000 | 0.267000 | 0.267000 | 0.000000 |
