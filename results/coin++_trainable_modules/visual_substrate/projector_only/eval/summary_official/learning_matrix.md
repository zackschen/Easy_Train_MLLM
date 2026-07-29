# CoIN++ Visual Substrate Evaluation

Primary metric: `primary_score`. Final average: **0.1839**; average forgetting on old tasks: **0.0147**; BWT: **0.0041**.

## Continual Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.2247 | 0.1970 | 0.0784 | 0.0987 | 0.0820 | 0.0578 |
| medical | 0.2341 | 0.2330 | 0.0970 | 0.1276 | 0.0820 | 0.0617 |
| document | 0.2526 | 0.2390 | 0.1763 | 0.1618 | 0.0990 | 0.0941 |
| infographic | 0.2762 | 0.2400 | 0.1908 | 0.1879 | 0.0930 | 0.1298 |
| diagram | 0.2878 | 0.2380 | 0.1881 | 0.1779 | 0.1090 | 0.1438 |
| chart | 0.2912 | 0.2240 | 0.1840 | 0.1371 | 0.1153 | 0.1519 |

## Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.2247 | 0.2912 | 0.2912 | 0.0000 | 0.0665 |
| medical | 0.2330 | 0.2400 | 0.2240 | 0.0160 | -0.0090 |
| document | 0.1763 | 0.1908 | 0.1840 | 0.0068 | 0.0077 |
| infographic | 0.1879 | 0.1879 | 0.1371 | 0.0507 | -0.0507 |
| diagram | 0.1090 | 0.1153 | 0.1153 | 0.0000 | 0.0063 |
| chart | 0.1519 | 0.1519 | 0.1519 | 0.0000 | 0.0000 |

## Scoring Coverage

| Trained until | Task | Official metric | LLM judge |
|---|---|---:|---:|
| natural_photo | natural_photo | 100.0% | 0.0% |
| natural_photo | medical | 100.0% | 0.0% |
| natural_photo | document | 100.0% | 0.0% |
| natural_photo | infographic | 100.0% | 0.0% |
| natural_photo | diagram | 100.0% | 0.0% |
| natural_photo | chart | 100.0% | 0.0% |
| medical | natural_photo | 100.0% | 0.0% |
| medical | medical | 100.0% | 0.0% |
| medical | document | 100.0% | 0.0% |
| medical | infographic | 100.0% | 0.0% |
| medical | diagram | 100.0% | 0.0% |
| medical | chart | 100.0% | 0.0% |
| document | natural_photo | 100.0% | 0.0% |
| document | medical | 100.0% | 0.0% |
| document | document | 100.0% | 0.0% |
| document | infographic | 100.0% | 0.0% |
| document | diagram | 100.0% | 0.0% |
| document | chart | 100.0% | 0.0% |
| infographic | natural_photo | 100.0% | 0.0% |
| infographic | medical | 100.0% | 0.0% |
| infographic | document | 100.0% | 0.0% |
| infographic | infographic | 100.0% | 0.0% |
| infographic | diagram | 100.0% | 0.0% |
| infographic | chart | 100.0% | 0.0% |
| diagram | natural_photo | 100.0% | 0.0% |
| diagram | medical | 100.0% | 0.0% |
| diagram | document | 100.0% | 0.0% |
| diagram | infographic | 100.0% | 0.0% |
| diagram | diagram | 100.0% | 0.0% |
| diagram | chart | 100.0% | 0.0% |
| chart | natural_photo | 100.0% | 0.0% |
| chart | medical | 100.0% | 0.0% |
| chart | document | 100.0% | 0.0% |
| chart | infographic | 100.0% | 0.0% |
| chart | diagram | 100.0% | 0.0% |
| chart | chart | 100.0% | 0.0% |
