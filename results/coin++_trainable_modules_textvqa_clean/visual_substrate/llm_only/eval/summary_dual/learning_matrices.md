# CoIN++ Visual Substrate Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.2902 | 0.3554 | 0.3197 | 0.0390 | -0.0354 |
| LLM Judge | 0.3040 | 0.3832 | 0.3215 | 0.0246 | -0.0209 |

## Standard Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.4329 | 0.2750 | 0.1831 | 0.1805 | 0.1830 | 0.1459 |
| medical | 0.4151 | 0.4370 | 0.1954 | 0.1963 | 0.1360 | 0.1170 |
| document | 0.4201 | 0.4340 | 0.2807 | 0.1988 | 0.1790 | 0.1541 |
| infographic | 0.3677 | 0.4140 | 0.2563 | 0.2477 | 0.1840 | 0.1417 |
| diagram | 0.4113 | 0.3370 | 0.2404 | 0.2306 | 0.1980 | 0.1528 |
| chart | 0.3809 | 0.4100 | 0.2342 | 0.1783 | 0.2160 | 0.3218 |

## LLM-Judge Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.4965 | 0.3160 | 0.1778 | 0.1702 | 0.2116 | 0.1436 |
| medical | 0.4871 | 0.4764 | 0.1625 | 0.1508 | 0.1673 | 0.1235 |
| document | 0.4855 | 0.4747 | 0.2150 | 0.1612 | 0.2064 | 0.1461 |
| infographic | 0.4333 | 0.4567 | 0.2160 | 0.2075 | 0.2124 | 0.1485 |
| diagram | 0.4663 | 0.3796 | 0.2009 | 0.1989 | 0.2387 | 0.1537 |
| chart | 0.4484 | 0.4565 | 0.1908 | 0.1777 | 0.2563 | 0.2946 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.4329 | 0.4329 | 0.3809 | 0.0520 | -0.0520 |
| medical | 0.4370 | 0.4370 | 0.4100 | 0.0270 | -0.0270 |
| document | 0.2807 | 0.2807 | 0.2342 | 0.0465 | -0.0465 |
| infographic | 0.2477 | 0.2477 | 0.1783 | 0.0694 | -0.0694 |
| diagram | 0.1980 | 0.2160 | 0.2160 | 0.0000 | 0.0180 |
| chart | 0.3218 | 0.3218 | 0.3218 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.4965 | 0.4965 | 0.4484 | 0.0481 | -0.0481 |
| medical | 0.4764 | 0.4764 | 0.4565 | 0.0200 | -0.0200 |
| document | 0.2150 | 0.2160 | 0.1908 | 0.0252 | -0.0242 |
| infographic | 0.2075 | 0.2075 | 0.1777 | 0.0298 | -0.0298 |
| diagram | 0.2387 | 0.2563 | 0.2563 | 0.0000 | 0.0176 |
| chart | 0.2946 | 0.2946 | 0.2946 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| natural_photo | natural_photo | 100.0% | 0.0% | 100.0% | 91.9% |
| natural_photo | medical | 100.0% | 0.0% | 100.0% | 94.3% |
| natural_photo | document | 100.0% | 0.0% | 100.0% | 84.4% |
| natural_photo | infographic | 100.0% | 0.0% | 100.0% | 86.4% |
| natural_photo | diagram | 100.0% | 0.0% | 100.0% | 92.8% |
| natural_photo | chart | 100.0% | 0.0% | 100.0% | 95.3% |
| medical | natural_photo | 100.0% | 0.0% | 100.0% | 90.1% |
| medical | medical | 100.0% | 0.0% | 100.0% | 94.7% |
| medical | document | 100.0% | 0.0% | 100.0% | 82.8% |
| medical | infographic | 100.0% | 0.0% | 100.0% | 82.1% |
| medical | diagram | 100.0% | 0.0% | 100.0% | 93.7% |
| medical | chart | 100.0% | 0.0% | 100.0% | 95.0% |
| document | natural_photo | 100.0% | 0.0% | 100.0% | 91.7% |
| document | medical | 100.0% | 0.0% | 100.0% | 94.4% |
| document | document | 100.0% | 0.0% | 100.0% | 80.3% |
| document | infographic | 100.0% | 0.0% | 100.0% | 85.4% |
| document | diagram | 100.0% | 0.0% | 100.0% | 94.8% |
| document | chart | 100.0% | 0.0% | 100.0% | 93.4% |
| infographic | natural_photo | 100.0% | 0.0% | 100.0% | 91.6% |
| infographic | medical | 100.0% | 0.0% | 100.0% | 94.5% |
| infographic | document | 100.0% | 0.0% | 100.0% | 80.9% |
| infographic | infographic | 100.0% | 0.0% | 100.0% | 84.9% |
| infographic | diagram | 100.0% | 0.0% | 100.0% | 95.8% |
| infographic | chart | 100.0% | 0.0% | 100.0% | 93.6% |
| diagram | natural_photo | 100.0% | 0.0% | 100.0% | 93.1% |
| diagram | medical | 100.0% | 0.0% | 100.0% | 94.4% |
| diagram | document | 100.0% | 0.0% | 100.0% | 82.8% |
| diagram | infographic | 100.0% | 0.0% | 100.0% | 85.3% |
| diagram | diagram | 100.0% | 0.0% | 100.0% | 95.0% |
| diagram | chart | 100.0% | 0.0% | 100.0% | 94.6% |
| chart | natural_photo | 100.0% | 0.0% | 100.0% | 91.1% |
| chart | medical | 100.0% | 0.0% | 100.0% | 93.3% |
| chart | document | 100.0% | 0.0% | 100.0% | 83.6% |
| chart | infographic | 100.0% | 0.0% | 100.0% | 89.8% |
| chart | diagram | 100.0% | 0.0% | 100.0% | 94.6% |
| chart | chart | 100.0% | 0.0% | 100.0% | 93.5% |
