# Factor-1 Visual Substrate Continual Evaluation (relaxed_match)

## Performance Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.293 | 0.287 | 0.135 | 0.137 | 0.128 | 0.073 |
| medical | 0.310 | 0.309 | 0.142 | 0.124 | 0.135 | 0.067 |
| document | 0.307 | 0.304 | 0.162 | 0.132 | 0.124 | 0.093 |
| infographic | 0.315 | 0.287 | 0.174 | 0.159 | 0.122 | 0.109 |
| diagram | 0.323 | 0.297 | 0.179 | 0.165 | 0.150 | 0.111 |
| chart | 0.278 | 0.291 | 0.172 | 0.161 | 0.146 | 0.171 |

## Forgetting

| Task | Score at learning | Best after learning | Final score | Forgetting |
|---|---:|---:|---:|---:|
| natural_photo | 0.293000 | 0.323000 | 0.278000 | 0.045000 |
| medical | 0.309000 | 0.309000 | 0.291000 | 0.018000 |
| document | 0.162000 | 0.179000 | 0.172000 | 0.007000 |
| infographic | 0.159000 | 0.165000 | 0.161000 | 0.004000 |
| diagram | 0.150000 | 0.150000 | 0.146000 | 0.004000 |
| chart | 0.171000 | 0.171000 | 0.171000 | 0.000000 |
