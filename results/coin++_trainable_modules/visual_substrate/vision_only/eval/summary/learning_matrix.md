# Factor-1 Visual Substrate Continual Evaluation (relaxed_match)

## Performance Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.238 | 0.245 | 0.083 | 0.101 | 0.111 | 0.054 |
| medical | 0.246 | 0.300 | 0.095 | 0.122 | 0.123 | 0.051 |
| document | 0.261 | 0.303 | 0.117 | 0.134 | 0.133 | 0.074 |
| infographic | 0.278 | 0.292 | 0.124 | 0.140 | 0.131 | 0.085 |
| diagram | 0.282 | 0.291 | 0.129 | 0.140 | 0.138 | 0.082 |
| chart | 0.254 | 0.289 | 0.136 | 0.141 | 0.122 | 0.161 |

## Forgetting

| Task | Score at learning | Best after learning | Final score | Forgetting |
|---|---:|---:|---:|---:|
| natural_photo | 0.238000 | 0.282000 | 0.254000 | 0.028000 |
| medical | 0.300000 | 0.303000 | 0.289000 | 0.014000 |
| document | 0.117000 | 0.136000 | 0.136000 | 0.000000 |
| infographic | 0.140000 | 0.141000 | 0.141000 | 0.000000 |
| diagram | 0.138000 | 0.138000 | 0.122000 | 0.016000 |
| chart | 0.161000 | 0.161000 | 0.161000 | 0.000000 |
