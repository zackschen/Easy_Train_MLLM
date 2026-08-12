# Factor-1 Visual Substrate Continual Evaluation (relaxed_match)

## Performance Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.251 | 0.277 | 0.100 | 0.130 | 0.116 | 0.065 |
| medical | 0.262 | 0.299 | 0.107 | 0.142 | 0.121 | 0.061 |
| document | 0.289 | 0.293 | 0.123 | 0.144 | 0.132 | 0.083 |
| infographic | 0.288 | 0.294 | 0.145 | 0.156 | 0.130 | 0.101 |
| diagram | 0.298 | 0.298 | 0.134 | 0.150 | 0.134 | 0.090 |
| chart | 0.266 | 0.291 | 0.152 | 0.139 | 0.132 | 0.173 |

## Forgetting

| Task | Score at learning | Best after learning | Final score | Forgetting |
|---|---:|---:|---:|---:|
| natural_photo | 0.251000 | 0.298000 | 0.266000 | 0.032000 |
| medical | 0.299000 | 0.299000 | 0.291000 | 0.008000 |
| document | 0.123000 | 0.152000 | 0.152000 | 0.000000 |
| infographic | 0.156000 | 0.156000 | 0.139000 | 0.017000 |
| diagram | 0.134000 | 0.134000 | 0.132000 | 0.002000 |
| chart | 0.173000 | 0.173000 | 0.173000 | 0.000000 |
