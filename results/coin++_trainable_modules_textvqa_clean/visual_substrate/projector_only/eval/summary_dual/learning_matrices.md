# CoIN++ Visual Substrate Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.1952 | 0.2320 | 0.1980 | 0.0146 | -0.0033 |
| LLM Judge | 0.2291 | 0.2827 | 0.2171 | 0.0013 | 0.0144 |

## Standard Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.2605 | 0.2240 | 0.1186 | 0.1310 | 0.0920 | 0.0734 |
| medical | 0.2604 | 0.2470 | 0.1350 | 0.1495 | 0.0970 | 0.0607 |
| document | 0.2902 | 0.2400 | 0.1926 | 0.1643 | 0.0920 | 0.1169 |
| infographic | 0.2999 | 0.2350 | 0.1996 | 0.1979 | 0.0840 | 0.1420 |
| diagram | 0.3071 | 0.2450 | 0.1965 | 0.1770 | 0.1170 | 0.1617 |
| chart | 0.2978 | 0.2390 | 0.2024 | 0.1450 | 0.1140 | 0.1729 |

## LLM-Judge Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.3632 | 0.2591 | 0.1246 | 0.1177 | 0.0954 | 0.0600 |
| medical | 0.3717 | 0.3026 | 0.1351 | 0.1336 | 0.1181 | 0.0616 |
| document | 0.3898 | 0.2894 | 0.1648 | 0.1266 | 0.1065 | 0.1073 |
| infographic | 0.3932 | 0.2778 | 0.1711 | 0.1604 | 0.1030 | 0.1366 |
| diagram | 0.3984 | 0.2948 | 0.1823 | 0.1614 | 0.1359 | 0.1461 |
| chart | 0.4125 | 0.2961 | 0.1855 | 0.1680 | 0.1366 | 0.1758 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.2605 | 0.3071 | 0.2978 | 0.0093 | 0.0373 |
| medical | 0.2470 | 0.2470 | 0.2390 | 0.0080 | -0.0080 |
| document | 0.1926 | 0.2024 | 0.2024 | 0.0000 | 0.0099 |
| infographic | 0.1979 | 0.1979 | 0.1450 | 0.0529 | -0.0529 |
| diagram | 0.1170 | 0.1170 | 0.1140 | 0.0030 | -0.0030 |
| chart | 0.1729 | 0.1729 | 0.1729 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.3632 | 0.4125 | 0.4125 | 0.0000 | 0.0493 |
| medical | 0.3026 | 0.3026 | 0.2961 | 0.0065 | -0.0065 |
| document | 0.1648 | 0.1855 | 0.1855 | 0.0000 | 0.0207 |
| infographic | 0.1604 | 0.1680 | 0.1680 | 0.0000 | 0.0076 |
| diagram | 0.1359 | 0.1366 | 0.1366 | 0.0000 | 0.0007 |
| chart | 0.1758 | 0.1758 | 0.1758 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| natural_photo | natural_photo | 100.0% | 0.0% | 100.0% | 87.1% |
| natural_photo | medical | 100.0% | 0.0% | 100.0% | 95.5% |
| natural_photo | document | 100.0% | 0.0% | 100.0% | 88.2% |
| natural_photo | infographic | 100.0% | 0.0% | 100.0% | 86.8% |
| natural_photo | diagram | 100.0% | 0.0% | 100.0% | 93.5% |
| natural_photo | chart | 100.0% | 0.0% | 100.0% | 96.0% |
| medical | natural_photo | 100.0% | 0.0% | 100.0% | 86.1% |
| medical | medical | 100.0% | 0.0% | 100.0% | 93.1% |
| medical | document | 100.0% | 0.0% | 100.0% | 87.4% |
| medical | infographic | 100.0% | 0.0% | 100.0% | 84.8% |
| medical | diagram | 100.0% | 0.0% | 100.0% | 92.0% |
| medical | chart | 100.0% | 0.0% | 100.0% | 96.2% |
| document | natural_photo | 100.0% | 0.0% | 100.0% | 87.2% |
| document | medical | 100.0% | 0.0% | 100.0% | 93.9% |
| document | document | 100.0% | 0.0% | 100.0% | 84.5% |
| document | infographic | 100.0% | 0.0% | 100.0% | 85.5% |
| document | diagram | 100.0% | 0.0% | 100.0% | 93.2% |
| document | chart | 100.0% | 0.0% | 100.0% | 95.2% |
| infographic | natural_photo | 100.0% | 0.0% | 100.0% | 88.0% |
| infographic | medical | 100.0% | 0.0% | 100.0% | 94.9% |
| infographic | document | 100.0% | 0.0% | 100.0% | 85.1% |
| infographic | infographic | 100.0% | 0.0% | 100.0% | 84.4% |
| infographic | diagram | 100.0% | 0.0% | 100.0% | 93.5% |
| infographic | chart | 100.0% | 0.0% | 100.0% | 94.8% |
| diagram | natural_photo | 100.0% | 0.0% | 100.0% | 88.7% |
| diagram | medical | 100.0% | 0.0% | 100.0% | 93.6% |
| diagram | document | 100.0% | 0.0% | 100.0% | 85.9% |
| diagram | infographic | 100.0% | 0.0% | 100.0% | 87.0% |
| diagram | diagram | 100.0% | 0.0% | 100.0% | 94.3% |
| diagram | chart | 100.0% | 0.0% | 100.0% | 95.6% |
| chart | natural_photo | 100.0% | 0.0% | 100.0% | 86.8% |
| chart | medical | 100.0% | 0.0% | 100.0% | 93.2% |
| chart | document | 100.0% | 0.0% | 100.0% | 85.4% |
| chart | infographic | 100.0% | 0.0% | 100.0% | 88.2% |
| chart | diagram | 100.0% | 0.0% | 100.0% | 93.6% |
| chart | chart | 100.0% | 0.0% | 100.0% | 93.5% |
