# CoIN++ Visual Substrate Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.3016 | 0.3584 | 0.3256 | 0.0378 | -0.0288 |
| LLM Judge | 0.3117 | 0.3845 | 0.3241 | 0.0248 | -0.0149 |

## Standard Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.4215 | 0.2830 | 0.1913 | 0.1810 | 0.1850 | 0.1416 |
| medical | 0.4009 | 0.4210 | 0.1680 | 0.1902 | 0.1180 | 0.1178 |
| document | 0.4041 | 0.4530 | 0.2851 | 0.1949 | 0.1500 | 0.1220 |
| infographic | 0.3739 | 0.4230 | 0.2732 | 0.2629 | 0.1810 | 0.1555 |
| diagram | 0.4035 | 0.4120 | 0.2467 | 0.2345 | 0.2140 | 0.1405 |
| chart | 0.3873 | 0.4240 | 0.2333 | 0.1891 | 0.2270 | 0.3492 |

## LLM-Judge Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.4871 | 0.3186 | 0.1742 | 0.1749 | 0.2211 | 0.1367 |
| medical | 0.4788 | 0.4562 | 0.1362 | 0.1516 | 0.1530 | 0.1258 |
| document | 0.4713 | 0.4895 | 0.2240 | 0.1546 | 0.1760 | 0.1126 |
| infographic | 0.4423 | 0.4597 | 0.2275 | 0.2112 | 0.2155 | 0.1544 |
| diagram | 0.4642 | 0.4469 | 0.1993 | 0.1854 | 0.2565 | 0.1290 |
| chart | 0.4470 | 0.4561 | 0.1966 | 0.1918 | 0.2691 | 0.3094 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.4215 | 0.4215 | 0.3873 | 0.0342 | -0.0342 |
| medical | 0.4210 | 0.4530 | 0.4240 | 0.0290 | 0.0030 |
| document | 0.2851 | 0.2851 | 0.2333 | 0.0518 | -0.0518 |
| infographic | 0.2629 | 0.2629 | 0.1891 | 0.0739 | -0.0739 |
| diagram | 0.2140 | 0.2270 | 0.2270 | 0.0000 | 0.0130 |
| chart | 0.3492 | 0.3492 | 0.3492 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.4871 | 0.4871 | 0.4470 | 0.0401 | -0.0401 |
| medical | 0.4562 | 0.4895 | 0.4561 | 0.0335 | -0.0002 |
| document | 0.2240 | 0.2275 | 0.1966 | 0.0309 | -0.0274 |
| infographic | 0.2112 | 0.2112 | 0.1918 | 0.0194 | -0.0194 |
| diagram | 0.2565 | 0.2691 | 0.2691 | 0.0000 | 0.0126 |
| chart | 0.3094 | 0.3094 | 0.3094 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| natural_photo | natural_photo | 100.0% | 0.0% | 100.0% | 91.2% |
| natural_photo | medical | 100.0% | 0.0% | 100.0% | 94.7% |
| natural_photo | document | 100.0% | 0.0% | 100.0% | 85.6% |
| natural_photo | infographic | 100.0% | 0.0% | 100.0% | 86.1% |
| natural_photo | diagram | 100.0% | 0.0% | 100.0% | 94.5% |
| natural_photo | chart | 100.0% | 0.0% | 100.0% | 94.0% |
| medical | natural_photo | 100.0% | 0.0% | 100.0% | 88.9% |
| medical | medical | 100.0% | 0.0% | 100.0% | 94.8% |
| medical | document | 100.0% | 0.0% | 100.0% | 85.6% |
| medical | infographic | 100.0% | 0.0% | 100.0% | 83.5% |
| medical | diagram | 100.0% | 0.0% | 100.0% | 93.7% |
| medical | chart | 100.0% | 0.0% | 100.0% | 94.0% |
| document | natural_photo | 100.0% | 0.0% | 100.0% | 91.2% |
| document | medical | 100.0% | 0.0% | 100.0% | 94.8% |
| document | document | 100.0% | 0.0% | 100.0% | 81.2% |
| document | infographic | 100.0% | 0.0% | 100.0% | 85.7% |
| document | diagram | 100.0% | 0.0% | 100.0% | 95.3% |
| document | chart | 100.0% | 0.0% | 100.0% | 93.0% |
| infographic | natural_photo | 100.0% | 0.0% | 100.0% | 90.9% |
| infographic | medical | 100.0% | 0.0% | 100.0% | 95.3% |
| infographic | document | 100.0% | 0.0% | 100.0% | 82.0% |
| infographic | infographic | 100.0% | 0.0% | 100.0% | 82.6% |
| infographic | diagram | 100.0% | 0.0% | 100.0% | 94.6% |
| infographic | chart | 100.0% | 0.0% | 100.0% | 93.5% |
| diagram | natural_photo | 100.0% | 0.0% | 100.0% | 92.6% |
| diagram | medical | 100.0% | 0.0% | 100.0% | 95.5% |
| diagram | document | 100.0% | 0.0% | 100.0% | 82.2% |
| diagram | infographic | 100.0% | 0.0% | 100.0% | 84.0% |
| diagram | diagram | 100.0% | 0.0% | 100.0% | 94.7% |
| diagram | chart | 100.0% | 0.0% | 100.0% | 93.8% |
| chart | natural_photo | 100.0% | 0.0% | 100.0% | 92.6% |
| chart | medical | 100.0% | 0.0% | 100.0% | 95.4% |
| chart | document | 100.0% | 0.0% | 100.0% | 83.2% |
| chart | infographic | 100.0% | 0.0% | 100.0% | 89.6% |
| chart | diagram | 100.0% | 0.0% | 100.0% | 94.3% |
| chart | chart | 100.0% | 0.0% | 100.0% | 92.7% |
