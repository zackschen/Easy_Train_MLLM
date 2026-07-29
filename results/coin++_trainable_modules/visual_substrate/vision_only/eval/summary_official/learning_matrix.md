# CoIN++ Visual Substrate Evaluation

Primary metric: `primary_score`. Final average: **0.1065**; average forgetting on old tasks: **0.0019**; BWT: **0.0511**.

## Continual Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.0396 | 0.0150 | 0.0079 | 0.0096 | 0.0220 | 0.0050 |
| medical | 0.0562 | 0.0540 | 0.0132 | 0.0279 | 0.0290 | 0.0167 |
| document | 0.0596 | 0.0840 | 0.0164 | 0.0265 | 0.0400 | 0.0185 |
| infographic | 0.0738 | 0.1350 | 0.0374 | 0.0817 | 0.0570 | 0.0395 |
| diagram | 0.0868 | 0.1700 | 0.0591 | 0.1020 | 0.0600 | 0.0510 |
| chart | 0.0824 | 0.1660 | 0.0757 | 0.1010 | 0.0820 | 0.1318 |

## Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.0396 | 0.0868 | 0.0824 | 0.0044 | 0.0428 |
| medical | 0.0540 | 0.1700 | 0.1660 | 0.0040 | 0.1120 |
| document | 0.0164 | 0.0757 | 0.0757 | 0.0000 | 0.0594 |
| infographic | 0.0817 | 0.1020 | 0.1010 | 0.0010 | 0.0193 |
| diagram | 0.0600 | 0.0820 | 0.0820 | 0.0000 | 0.0220 |
| chart | 0.1318 | 0.1318 | 0.1318 | 0.0000 | 0.0000 |

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
