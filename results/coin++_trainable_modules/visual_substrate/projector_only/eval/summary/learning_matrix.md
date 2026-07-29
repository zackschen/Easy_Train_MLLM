# Factor-1 Visual Substrate Continual Evaluation (relaxed_match)

## Performance Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.289 | 0.262 | 0.116 | 0.131 | 0.129 | 0.066 |
| medical | 0.293 | 0.296 | 0.118 | 0.123 | 0.127 | 0.071 |
| document | 0.297 | 0.304 | 0.156 | 0.126 | 0.137 | 0.090 |
| infographic | 0.307 | 0.293 | 0.163 | 0.148 | 0.131 | 0.102 |
| diagram | 0.315 | 0.291 | 0.167 | 0.159 | 0.148 | 0.114 |
| chart | 0.279 | 0.276 | 0.165 | 0.151 | 0.137 | 0.166 |

## Forgetting

| Task | Score at learning | Best after learning | Final score | Forgetting |
|---|---:|---:|---:|---:|
| natural_photo | 0.289000 | 0.315000 | 0.279000 | 0.036000 |
| medical | 0.296000 | 0.304000 | 0.276000 | 0.028000 |
| document | 0.156000 | 0.167000 | 0.165000 | 0.002000 |
| infographic | 0.148000 | 0.159000 | 0.151000 | 0.008000 |
| diagram | 0.148000 | 0.148000 | 0.137000 | 0.011000 |
| chart | 0.166000 | 0.166000 | 0.166000 | 0.000000 |
