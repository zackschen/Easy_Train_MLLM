# CoIN++ Visual Substrate Evaluation

Primary metric: `primary_score`. Final average: **0.2844**; average forgetting on old tasks: **0.0482**; BWT: **-0.0482**.

## Continual Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.4435 | 0.2860 | 0.1986 | 0.1828 | 0.1760 | 0.1552 |
| medical | 0.4254 | 0.4510 | 0.1961 | 0.2133 | 0.1770 | 0.1417 |
| document | 0.4154 | 0.4200 | 0.2884 | 0.2071 | 0.1550 | 0.1523 |
| infographic | 0.3861 | 0.3940 | 0.2649 | 0.2409 | 0.1650 | 0.1499 |
| diagram | 0.3953 | 0.4000 | 0.2521 | 0.2305 | 0.2380 | 0.1402 |
| chart | 0.3902 | 0.3980 | 0.2313 | 0.1763 | 0.2250 | 0.2855 |

## Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.4435 | 0.4435 | 0.3902 | 0.0533 | -0.0533 |
| medical | 0.4510 | 0.4510 | 0.3980 | 0.0530 | -0.0530 |
| document | 0.2884 | 0.2884 | 0.2313 | 0.0570 | -0.0570 |
| infographic | 0.2409 | 0.2409 | 0.1763 | 0.0647 | -0.0647 |
| diagram | 0.2380 | 0.2380 | 0.2250 | 0.0130 | -0.0130 |
| chart | 0.2855 | 0.2855 | 0.2855 | 0.0000 | 0.0000 |

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
