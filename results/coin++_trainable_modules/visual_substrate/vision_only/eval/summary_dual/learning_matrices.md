# CoIN++ Visual Substrate Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.1065 | 0.0720 | 0.0639 | 0.0019 | 0.0511 |
| LLM Judge | 0.1928 | 0.2362 | 0.1747 | 0.0040 | 0.0217 |

## Standard Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.0396 | 0.0150 | 0.0079 | 0.0096 | 0.0220 | 0.0050 |
| medical | 0.0562 | 0.0540 | 0.0132 | 0.0279 | 0.0290 | 0.0167 |
| document | 0.0596 | 0.0840 | 0.0164 | 0.0265 | 0.0400 | 0.0185 |
| infographic | 0.0738 | 0.1350 | 0.0374 | 0.0817 | 0.0570 | 0.0395 |
| diagram | 0.0868 | 0.1700 | 0.0591 | 0.1020 | 0.0600 | 0.0510 |
| chart | 0.0824 | 0.1660 | 0.0757 | 0.1010 | 0.0820 | 0.1318 |

## LLM-Judge Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.2781 | 0.2013 | 0.0816 | 0.0712 | 0.0693 | 0.0167 |
| medical | 0.3033 | 0.2615 | 0.0946 | 0.0831 | 0.0855 | 0.0188 |
| document | 0.3236 | 0.2804 | 0.1218 | 0.1089 | 0.0950 | 0.0412 |
| infographic | 0.3530 | 0.2804 | 0.1258 | 0.1276 | 0.1066 | 0.0647 |
| diagram | 0.3501 | 0.2830 | 0.1375 | 0.1219 | 0.1090 | 0.0710 |
| chart | 0.3378 | 0.2810 | 0.1347 | 0.1442 | 0.1090 | 0.1504 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.0396 | 0.0868 | 0.0824 | 0.0044 | 0.0428 |
| medical | 0.0540 | 0.1700 | 0.1660 | 0.0040 | 0.1120 |
| document | 0.0164 | 0.0757 | 0.0757 | 0.0000 | 0.0594 |
| infographic | 0.0817 | 0.1020 | 0.1010 | 0.0010 | 0.0193 |
| diagram | 0.0600 | 0.0820 | 0.0820 | 0.0000 | 0.0220 |
| chart | 0.1318 | 0.1318 | 0.1318 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.2781 | 0.3530 | 0.3378 | 0.0152 | 0.0597 |
| medical | 0.2615 | 0.2830 | 0.2810 | 0.0020 | 0.0195 |
| document | 0.1218 | 0.1375 | 0.1347 | 0.0028 | 0.0129 |
| infographic | 0.1276 | 0.1442 | 0.1442 | 0.0000 | 0.0166 |
| diagram | 0.1090 | 0.1090 | 0.1090 | 0.0000 | 0.0000 |
| chart | 0.1504 | 0.1504 | 0.1504 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| natural_photo | natural_photo | 100.0% | 0.0% | 100.0% | 73.9% |
| natural_photo | medical | 100.0% | 0.0% | 100.0% | 80.0% |
| natural_photo | document | 100.0% | 0.0% | 100.0% | 91.0% |
| natural_photo | infographic | 100.0% | 0.0% | 100.0% | 91.1% |
| natural_photo | diagram | 100.0% | 0.0% | 100.0% | 91.2% |
| natural_photo | chart | 100.0% | 0.0% | 100.0% | 97.8% |
| medical | natural_photo | 100.0% | 0.0% | 100.0% | 73.4% |
| medical | medical | 100.0% | 0.0% | 100.0% | 77.8% |
| medical | document | 100.0% | 0.0% | 100.0% | 90.3% |
| medical | infographic | 100.0% | 0.0% | 100.0% | 88.7% |
| medical | diagram | 100.0% | 0.0% | 100.0% | 90.5% |
| medical | chart | 100.0% | 0.0% | 100.0% | 96.5% |
| document | natural_photo | 100.0% | 0.0% | 100.0% | 71.6% |
| document | medical | 100.0% | 0.0% | 100.0% | 78.6% |
| document | document | 100.0% | 0.0% | 100.0% | 87.1% |
| document | infographic | 100.0% | 0.0% | 100.0% | 87.6% |
| document | diagram | 100.0% | 0.0% | 100.0% | 90.1% |
| document | chart | 100.0% | 0.0% | 100.0% | 94.3% |
| infographic | natural_photo | 100.0% | 0.0% | 100.0% | 70.2% |
| infographic | medical | 100.0% | 0.0% | 100.0% | 83.6% |
| infographic | document | 100.0% | 0.0% | 100.0% | 86.2% |
| infographic | infographic | 100.0% | 0.0% | 100.0% | 85.2% |
| infographic | diagram | 100.0% | 0.0% | 100.0% | 90.5% |
| infographic | chart | 100.0% | 0.0% | 100.0% | 93.0% |
| diagram | natural_photo | 100.0% | 0.0% | 100.0% | 71.7% |
| diagram | medical | 100.0% | 0.0% | 100.0% | 86.9% |
| diagram | document | 100.0% | 0.0% | 100.0% | 84.4% |
| diagram | infographic | 100.0% | 0.0% | 100.0% | 84.8% |
| diagram | diagram | 100.0% | 0.0% | 100.0% | 90.9% |
| diagram | chart | 100.0% | 0.0% | 100.0% | 92.9% |
| chart | natural_photo | 100.0% | 0.0% | 100.0% | 72.6% |
| chart | medical | 100.0% | 0.0% | 100.0% | 86.9% |
| chart | document | 100.0% | 0.0% | 100.0% | 84.2% |
| chart | infographic | 100.0% | 0.0% | 100.0% | 83.6% |
| chart | diagram | 100.0% | 0.0% | 100.0% | 93.4% |
| chart | chart | 100.0% | 0.0% | 100.0% | 94.1% |
