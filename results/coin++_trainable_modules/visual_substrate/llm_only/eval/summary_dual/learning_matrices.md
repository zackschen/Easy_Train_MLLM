# CoIN++ Visual Substrate Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.2844 | 0.3609 | 0.3246 | 0.0482 | -0.0482 |
| LLM Judge | 0.2963 | 0.3877 | 0.3215 | 0.0304 | -0.0302 |

## Standard Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.4435 | 0.2860 | 0.1986 | 0.1828 | 0.1760 | 0.1552 |
| medical | 0.4254 | 0.4510 | 0.1961 | 0.2133 | 0.1770 | 0.1417 |
| document | 0.4154 | 0.4200 | 0.2884 | 0.2071 | 0.1550 | 0.1523 |
| infographic | 0.3861 | 0.3940 | 0.2649 | 0.2409 | 0.1650 | 0.1499 |
| diagram | 0.3953 | 0.4000 | 0.2521 | 0.2305 | 0.2380 | 0.1402 |
| chart | 0.3902 | 0.3980 | 0.2313 | 0.1763 | 0.2250 | 0.2855 |

## LLM-Judge Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.5118 | 0.3286 | 0.1849 | 0.1707 | 0.2116 | 0.1593 |
| medical | 0.4873 | 0.4872 | 0.1732 | 0.1744 | 0.2203 | 0.1477 |
| document | 0.4902 | 0.4551 | 0.2205 | 0.1680 | 0.1807 | 0.1485 |
| infographic | 0.4518 | 0.4432 | 0.2175 | 0.1940 | 0.2027 | 0.1512 |
| diagram | 0.4623 | 0.4350 | 0.2209 | 0.1944 | 0.2658 | 0.1433 |
| chart | 0.4468 | 0.4286 | 0.2100 | 0.1878 | 0.2550 | 0.2496 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.4435 | 0.4435 | 0.3902 | 0.0533 | -0.0533 |
| medical | 0.4510 | 0.4510 | 0.3980 | 0.0530 | -0.0530 |
| document | 0.2884 | 0.2884 | 0.2313 | 0.0570 | -0.0570 |
| infographic | 0.2409 | 0.2409 | 0.1763 | 0.0647 | -0.0647 |
| diagram | 0.2380 | 0.2380 | 0.2250 | 0.0130 | -0.0130 |
| chart | 0.2855 | 0.2855 | 0.2855 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.5118 | 0.5118 | 0.4468 | 0.0650 | -0.0650 |
| medical | 0.4872 | 0.4872 | 0.4286 | 0.0586 | -0.0586 |
| document | 0.2205 | 0.2209 | 0.2100 | 0.0109 | -0.0105 |
| infographic | 0.1940 | 0.1944 | 0.1878 | 0.0066 | -0.0062 |
| diagram | 0.2658 | 0.2658 | 0.2550 | 0.0108 | -0.0108 |
| chart | 0.2496 | 0.2496 | 0.2496 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| natural_photo | natural_photo | 100.0% | 0.0% | 100.0% | 91.8% |
| natural_photo | medical | 100.0% | 0.0% | 100.0% | 94.1% |
| natural_photo | document | 100.0% | 0.0% | 100.0% | 85.5% |
| natural_photo | infographic | 100.0% | 0.0% | 100.0% | 85.2% |
| natural_photo | diagram | 100.0% | 0.0% | 100.0% | 93.2% |
| natural_photo | chart | 100.0% | 0.0% | 100.0% | 93.6% |
| medical | natural_photo | 100.0% | 0.0% | 100.0% | 90.6% |
| medical | medical | 100.0% | 0.0% | 100.0% | 94.9% |
| medical | document | 100.0% | 0.0% | 100.0% | 84.4% |
| medical | infographic | 100.0% | 0.0% | 100.0% | 83.4% |
| medical | diagram | 100.0% | 0.0% | 100.0% | 92.2% |
| medical | chart | 100.0% | 0.0% | 100.0% | 95.7% |
| document | natural_photo | 100.0% | 0.0% | 100.0% | 90.3% |
| document | medical | 100.0% | 0.0% | 100.0% | 95.1% |
| document | document | 100.0% | 0.0% | 100.0% | 80.1% |
| document | infographic | 100.0% | 0.0% | 100.0% | 85.8% |
| document | diagram | 100.0% | 0.0% | 100.0% | 92.8% |
| document | chart | 100.0% | 0.0% | 100.0% | 93.7% |
| infographic | natural_photo | 100.0% | 0.0% | 100.0% | 91.1% |
| infographic | medical | 100.0% | 0.0% | 100.0% | 94.0% |
| infographic | document | 100.0% | 0.0% | 100.0% | 80.1% |
| infographic | infographic | 100.0% | 0.0% | 100.0% | 84.2% |
| infographic | diagram | 100.0% | 0.0% | 100.0% | 94.3% |
| infographic | chart | 100.0% | 0.0% | 100.0% | 93.5% |
| diagram | natural_photo | 100.0% | 0.0% | 100.0% | 90.8% |
| diagram | medical | 100.0% | 0.0% | 100.0% | 94.6% |
| diagram | document | 100.0% | 0.0% | 100.0% | 80.5% |
| diagram | infographic | 100.0% | 0.0% | 100.0% | 84.2% |
| diagram | diagram | 100.0% | 0.0% | 100.0% | 95.0% |
| diagram | chart | 100.0% | 0.0% | 100.0% | 93.9% |
| chart | natural_photo | 100.0% | 0.0% | 100.0% | 92.5% |
| chart | medical | 100.0% | 0.0% | 100.0% | 95.4% |
| chart | document | 100.0% | 0.0% | 100.0% | 83.6% |
| chart | infographic | 100.0% | 0.0% | 100.0% | 90.4% |
| chart | diagram | 100.0% | 0.0% | 100.0% | 95.7% |
| chart | chart | 100.0% | 0.0% | 100.0% | 93.2% |
