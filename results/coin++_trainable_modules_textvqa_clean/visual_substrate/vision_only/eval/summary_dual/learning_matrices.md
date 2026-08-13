# CoIN++ Visual Substrate Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.1298 | 0.0994 | 0.0882 | 0.0066 | 0.0500 |
| LLM Judge | 0.2019 | 0.2555 | 0.1922 | 0.0026 | 0.0116 |

## Standard Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.0596 | 0.0400 | 0.0129 | 0.0212 | 0.0300 | 0.0095 |
| medical | 0.0722 | 0.1130 | 0.0204 | 0.0448 | 0.0420 | 0.0232 |
| document | 0.0808 | 0.1140 | 0.0191 | 0.0464 | 0.0450 | 0.0295 |
| infographic | 0.1078 | 0.1690 | 0.0615 | 0.1183 | 0.0610 | 0.0575 |
| diagram | 0.1325 | 0.2120 | 0.0840 | 0.1368 | 0.0790 | 0.0581 |
| chart | 0.1084 | 0.2160 | 0.0955 | 0.1280 | 0.0910 | 0.1400 |

## LLM-Judge Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.3319 | 0.2446 | 0.1089 | 0.0900 | 0.0863 | 0.0278 |
| medical | 0.3342 | 0.2826 | 0.1077 | 0.1012 | 0.0968 | 0.0280 |
| document | 0.3535 | 0.2810 | 0.1287 | 0.1168 | 0.1045 | 0.0592 |
| infographic | 0.3622 | 0.2828 | 0.1432 | 0.1284 | 0.1082 | 0.0805 |
| diagram | 0.3663 | 0.2892 | 0.1318 | 0.1337 | 0.1161 | 0.0844 |
| chart | 0.3550 | 0.2900 | 0.1441 | 0.1423 | 0.1144 | 0.1654 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.0596 | 0.1325 | 0.1084 | 0.0241 | 0.0488 |
| medical | 0.1130 | 0.2160 | 0.2160 | 0.0000 | 0.1030 |
| document | 0.0191 | 0.0955 | 0.0955 | 0.0000 | 0.0765 |
| infographic | 0.1183 | 0.1368 | 0.1280 | 0.0088 | 0.0097 |
| diagram | 0.0790 | 0.0910 | 0.0910 | 0.0000 | 0.0120 |
| chart | 0.1400 | 0.1400 | 0.1400 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.3319 | 0.3663 | 0.3550 | 0.0113 | 0.0231 |
| medical | 0.2826 | 0.2900 | 0.2900 | 0.0000 | 0.0074 |
| document | 0.1287 | 0.1441 | 0.1441 | 0.0000 | 0.0154 |
| infographic | 0.1284 | 0.1423 | 0.1423 | 0.0000 | 0.0139 |
| diagram | 0.1161 | 0.1161 | 0.1144 | 0.0017 | -0.0017 |
| chart | 0.1654 | 0.1654 | 0.1654 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| natural_photo | natural_photo | 100.0% | 0.0% | 100.0% | 70.5% |
| natural_photo | medical | 100.0% | 0.0% | 100.0% | 78.2% |
| natural_photo | document | 100.0% | 0.0% | 100.0% | 88.2% |
| natural_photo | infographic | 100.0% | 0.0% | 100.0% | 88.9% |
| natural_photo | diagram | 100.0% | 0.0% | 100.0% | 90.4% |
| natural_photo | chart | 100.0% | 0.0% | 100.0% | 96.1% |
| medical | natural_photo | 100.0% | 0.0% | 100.0% | 71.9% |
| medical | medical | 100.0% | 0.0% | 100.0% | 81.2% |
| medical | document | 100.0% | 0.0% | 100.0% | 88.7% |
| medical | infographic | 100.0% | 0.0% | 100.0% | 87.8% |
| medical | diagram | 100.0% | 0.0% | 100.0% | 90.4% |
| medical | chart | 100.0% | 0.0% | 100.0% | 95.8% |
| document | natural_photo | 100.0% | 0.0% | 100.0% | 71.2% |
| document | medical | 100.0% | 0.0% | 100.0% | 81.5% |
| document | document | 100.0% | 0.0% | 100.0% | 86.8% |
| document | infographic | 100.0% | 0.0% | 100.0% | 86.0% |
| document | diagram | 100.0% | 0.0% | 100.0% | 89.6% |
| document | chart | 100.0% | 0.0% | 100.0% | 93.3% |
| infographic | natural_photo | 100.0% | 0.0% | 100.0% | 72.5% |
| infographic | medical | 100.0% | 0.0% | 100.0% | 87.0% |
| infographic | document | 100.0% | 0.0% | 100.0% | 85.0% |
| infographic | infographic | 100.0% | 0.0% | 100.0% | 85.4% |
| infographic | diagram | 100.0% | 0.0% | 100.0% | 90.5% |
| infographic | chart | 100.0% | 0.0% | 100.0% | 92.8% |
| diagram | natural_photo | 100.0% | 0.0% | 100.0% | 74.6% |
| diagram | medical | 100.0% | 0.0% | 100.0% | 90.8% |
| diagram | document | 100.0% | 0.0% | 100.0% | 86.9% |
| diagram | infographic | 100.0% | 0.0% | 100.0% | 84.9% |
| diagram | diagram | 100.0% | 0.0% | 100.0% | 90.8% |
| diagram | chart | 100.0% | 0.0% | 100.0% | 93.4% |
| chart | natural_photo | 100.0% | 0.0% | 100.0% | 73.7% |
| chart | medical | 100.0% | 0.0% | 100.0% | 90.8% |
| chart | document | 100.0% | 0.0% | 100.0% | 82.9% |
| chart | infographic | 100.0% | 0.0% | 100.0% | 86.6% |
| chart | diagram | 100.0% | 0.0% | 100.0% | 92.4% |
| chart | chart | 100.0% | 0.0% | 100.0% | 92.7% |
