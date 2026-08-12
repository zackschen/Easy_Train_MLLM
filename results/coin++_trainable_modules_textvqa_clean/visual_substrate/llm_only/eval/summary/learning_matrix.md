# Factor-1 Visual Substrate Continual Evaluation (relaxed_match)

## Performance Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.474 | 0.295 | 0.209 | 0.181 | 0.208 | 0.116 |
| medical | 0.431 | 0.463 | 0.204 | 0.161 | 0.190 | 0.116 |
| document | 0.453 | 0.462 | 0.221 | 0.168 | 0.216 | 0.109 |
| infographic | 0.401 | 0.437 | 0.224 | 0.205 | 0.230 | 0.107 |
| diagram | 0.453 | 0.361 | 0.210 | 0.197 | 0.256 | 0.116 |
| chart | 0.411 | 0.442 | 0.199 | 0.177 | 0.259 | 0.296 |

## Forgetting

| Task | Score at learning | Best after learning | Final score | Forgetting |
|---|---:|---:|---:|---:|
| natural_photo | 0.474000 | 0.474000 | 0.411000 | 0.063000 |
| medical | 0.463000 | 0.463000 | 0.442000 | 0.021000 |
| document | 0.221000 | 0.224000 | 0.199000 | 0.025000 |
| infographic | 0.205000 | 0.205000 | 0.177000 | 0.028000 |
| diagram | 0.256000 | 0.259000 | 0.259000 | 0.000000 |
| chart | 0.296000 | 0.296000 | 0.296000 | 0.000000 |
