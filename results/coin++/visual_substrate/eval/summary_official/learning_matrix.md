# CoIN++ Visual Substrate Evaluation

Primary metric: `primary_score`. Final average: **0.1857**; average forgetting on old tasks: **0.0720**; BWT: **-0.0720**.

## Continual Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.4269 | 0.2760 | 0.1941 | 0.1743 | 0.1770 | 0.1407 |
| medical | 0.2012 | 0.3390 | 0.0628 | 0.1423 | 0.1100 | 0.0947 |
| document | 0.2546 | 0.3010 | 0.1010 | 0.1688 | 0.1270 | 0.0828 |
| infographic | 0.2249 | 0.2690 | 0.0716 | 0.1963 | 0.1013 | 0.0850 |
| diagram | 0.2377 | 0.3050 | 0.0708 | 0.1647 | 0.2190 | 0.0772 |
| chart | 0.2095 | 0.3040 | 0.0588 | 0.1508 | 0.1990 | 0.1921 |

## Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.4269 | 0.4269 | 0.2095 | 0.2174 | -0.2174 |
| medical | 0.3390 | 0.3390 | 0.3040 | 0.0350 | -0.0350 |
| document | 0.1010 | 0.1010 | 0.0588 | 0.0422 | -0.0422 |
| infographic | 0.1963 | 0.1963 | 0.1508 | 0.0455 | -0.0455 |
| diagram | 0.2190 | 0.2190 | 0.1990 | 0.0200 | -0.0200 |
| chart | 0.1921 | 0.1921 | 0.1921 | 0.0000 | 0.0000 |

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
