# CoIN++ Visual Substrate Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.1839 | 0.2148 | 0.1804 | 0.0147 | 0.0041 |
| LLM Judge | 0.2199 | 0.2760 | 0.2087 | 0.0021 | 0.0134 |

## Standard Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.2247 | 0.1970 | 0.0784 | 0.0987 | 0.0820 | 0.0578 |
| medical | 0.2341 | 0.2330 | 0.0970 | 0.1276 | 0.0820 | 0.0617 |
| document | 0.2526 | 0.2390 | 0.1763 | 0.1618 | 0.0990 | 0.0941 |
| infographic | 0.2762 | 0.2400 | 0.1908 | 0.1879 | 0.0930 | 0.1298 |
| diagram | 0.2878 | 0.2380 | 0.1881 | 0.1779 | 0.1090 | 0.1438 |
| chart | 0.2912 | 0.2240 | 0.1840 | 0.1371 | 0.1153 | 0.1519 |

## LLM-Judge Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.3570 | 0.2413 | 0.1127 | 0.0995 | 0.0951 | 0.0446 |
| medical | 0.3717 | 0.2942 | 0.1153 | 0.1242 | 0.1018 | 0.0548 |
| document | 0.3731 | 0.2920 | 0.1580 | 0.1249 | 0.1146 | 0.0953 |
| infographic | 0.3826 | 0.2898 | 0.1653 | 0.1506 | 0.1095 | 0.1275 |
| diagram | 0.3911 | 0.2906 | 0.1684 | 0.1488 | 0.1237 | 0.1379 |
| chart | 0.4041 | 0.2836 | 0.1744 | 0.1581 | 0.1304 | 0.1689 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.2247 | 0.2912 | 0.2912 | 0.0000 | 0.0665 |
| medical | 0.2330 | 0.2400 | 0.2240 | 0.0160 | -0.0090 |
| document | 0.1763 | 0.1908 | 0.1840 | 0.0068 | 0.0077 |
| infographic | 0.1879 | 0.1879 | 0.1371 | 0.0507 | -0.0507 |
| diagram | 0.1090 | 0.1153 | 0.1153 | 0.0000 | 0.0063 |
| chart | 0.1519 | 0.1519 | 0.1519 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.3570 | 0.4041 | 0.4041 | 0.0000 | 0.0471 |
| medical | 0.2942 | 0.2942 | 0.2836 | 0.0106 | -0.0106 |
| document | 0.1580 | 0.1744 | 0.1744 | 0.0000 | 0.0164 |
| infographic | 0.1506 | 0.1581 | 0.1581 | 0.0000 | 0.0075 |
| diagram | 0.1237 | 0.1304 | 0.1304 | 0.0000 | 0.0067 |
| chart | 0.1689 | 0.1689 | 0.1689 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| natural_photo | natural_photo | 100.0% | 0.0% | 100.0% | 83.9% |
| natural_photo | medical | 100.0% | 0.0% | 100.0% | 94.6% |
| natural_photo | document | 100.0% | 0.0% | 100.0% | 88.5% |
| natural_photo | infographic | 100.0% | 0.0% | 100.0% | 87.0% |
| natural_photo | diagram | 100.0% | 0.0% | 100.0% | 92.7% |
| natural_photo | chart | 100.0% | 0.0% | 100.0% | 96.3% |
| medical | natural_photo | 100.0% | 0.0% | 100.0% | 83.4% |
| medical | medical | 100.0% | 0.0% | 100.0% | 92.4% |
| medical | document | 100.0% | 0.0% | 100.0% | 87.8% |
| medical | infographic | 100.0% | 0.0% | 100.0% | 85.6% |
| medical | diagram | 100.0% | 0.0% | 100.0% | 92.2% |
| medical | chart | 100.0% | 0.0% | 100.0% | 96.1% |
| document | natural_photo | 100.0% | 0.0% | 100.0% | 85.4% |
| document | medical | 100.0% | 0.0% | 100.0% | 93.6% |
| document | document | 100.0% | 0.0% | 100.0% | 84.7% |
| document | infographic | 100.0% | 0.0% | 100.0% | 84.6% |
| document | diagram | 100.0% | 0.0% | 100.0% | 92.8% |
| document | chart | 100.0% | 0.0% | 100.0% | 95.2% |
| infographic | natural_photo | 100.0% | 0.0% | 100.0% | 86.8% |
| infographic | medical | 100.0% | 0.0% | 100.0% | 93.7% |
| infographic | document | 100.0% | 0.0% | 100.0% | 84.8% |
| infographic | infographic | 100.0% | 0.0% | 100.0% | 84.3% |
| infographic | diagram | 100.0% | 0.0% | 100.0% | 93.6% |
| infographic | chart | 100.0% | 0.0% | 100.0% | 94.9% |
| diagram | natural_photo | 100.0% | 0.0% | 100.0% | 87.4% |
| diagram | medical | 100.0% | 0.0% | 100.0% | 93.3% |
| diagram | document | 100.0% | 0.0% | 100.0% | 85.5% |
| diagram | infographic | 100.0% | 0.0% | 100.0% | 86.7% |
| diagram | diagram | 100.0% | 0.0% | 100.0% | 94.4% |
| diagram | chart | 100.0% | 0.0% | 100.0% | 95.3% |
| chart | natural_photo | 100.0% | 0.0% | 100.0% | 86.5% |
| chart | medical | 100.0% | 0.0% | 100.0% | 92.7% |
| chart | document | 100.0% | 0.0% | 100.0% | 85.7% |
| chart | infographic | 100.0% | 0.0% | 100.0% | 88.6% |
| chart | diagram | 100.0% | 0.0% | 100.0% | 94.1% |
| chart | chart | 100.0% | 0.0% | 100.0% | 93.6% |
