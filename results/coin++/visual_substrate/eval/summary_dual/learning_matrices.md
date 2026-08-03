# CoIN++ Visual Substrate Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.1857 | 0.2486 | 0.2457 | 0.0720 | -0.0720 |
| LLM Judge | 0.1903 | 0.2692 | 0.2500 | 0.0721 | -0.0717 |

## Standard Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.4269 | 0.2760 | 0.1941 | 0.1743 | 0.1770 | 0.1407 |
| medical | 0.2012 | 0.3390 | 0.0628 | 0.1423 | 0.1100 | 0.0947 |
| document | 0.2546 | 0.3010 | 0.1010 | 0.1688 | 0.1270 | 0.0828 |
| infographic | 0.2249 | 0.2690 | 0.0716 | 0.1963 | 0.1013 | 0.0850 |
| diagram | 0.2377 | 0.3050 | 0.0708 | 0.1647 | 0.2190 | 0.0772 |
| chart | 0.2095 | 0.3040 | 0.0588 | 0.1508 | 0.1990 | 0.1921 |

## LLM-Judge Score Matrix

| Trained until | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| natural_photo | 0.4932 | 0.3135 | 0.1818 | 0.1637 | 0.2237 | 0.1437 |
| medical | 0.2236 | 0.3664 | 0.0430 | 0.0979 | 0.1493 | 0.0927 |
| document | 0.2899 | 0.3212 | 0.0780 | 0.1315 | 0.1390 | 0.0871 |
| infographic | 0.2559 | 0.3013 | 0.0698 | 0.1510 | 0.1457 | 0.0843 |
| diagram | 0.2714 | 0.3221 | 0.0665 | 0.1530 | 0.2507 | 0.0757 |
| chart | 0.2326 | 0.3206 | 0.0601 | 0.1440 | 0.2237 | 0.1609 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.4269 | 0.4269 | 0.2095 | 0.2174 | -0.2174 |
| medical | 0.3390 | 0.3390 | 0.3040 | 0.0350 | -0.0350 |
| document | 0.1010 | 0.1010 | 0.0588 | 0.0422 | -0.0422 |
| infographic | 0.1963 | 0.1963 | 0.1508 | 0.0455 | -0.0455 |
| diagram | 0.2190 | 0.2190 | 0.1990 | 0.0200 | -0.0200 |
| chart | 0.1921 | 0.1921 | 0.1921 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| natural_photo | 0.4932 | 0.4932 | 0.2326 | 0.2606 | -0.2606 |
| medical | 0.3664 | 0.3664 | 0.3206 | 0.0458 | -0.0458 |
| document | 0.0780 | 0.0780 | 0.0601 | 0.0179 | -0.0179 |
| infographic | 0.1510 | 0.1530 | 0.1440 | 0.0090 | -0.0070 |
| diagram | 0.2507 | 0.2507 | 0.2237 | 0.0270 | -0.0270 |
| chart | 0.1609 | 0.1609 | 0.1609 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| natural_photo | natural_photo | 100.0% | 0.0% | 100.0% | 91.4% |
| natural_photo | medical | 100.0% | 0.0% | 100.0% | 94.9% |
| natural_photo | document | 100.0% | 0.0% | 100.0% | 84.4% |
| natural_photo | infographic | 100.0% | 0.0% | 100.0% | 86.1% |
| natural_photo | diagram | 100.0% | 0.0% | 100.0% | 93.6% |
| natural_photo | chart | 100.0% | 0.0% | 100.0% | 94.4% |
| medical | natural_photo | 100.0% | 0.0% | 100.0% | 95.9% |
| medical | medical | 100.0% | 0.0% | 100.0% | 96.6% |
| medical | document | 100.0% | 0.0% | 100.0% | 94.0% |
| medical | infographic | 100.0% | 0.0% | 100.0% | 85.3% |
| medical | diagram | 100.0% | 0.0% | 100.0% | 92.0% |
| medical | chart | 100.0% | 0.0% | 100.0% | 95.1% |
| document | natural_photo | 100.0% | 0.0% | 100.0% | 94.8% |
| document | medical | 100.0% | 0.0% | 100.0% | 96.7% |
| document | document | 100.0% | 0.0% | 100.0% | 92.4% |
| document | infographic | 100.0% | 0.0% | 100.0% | 84.4% |
| document | diagram | 100.0% | 0.0% | 100.0% | 94.1% |
| document | chart | 100.0% | 0.0% | 100.0% | 94.2% |
| infographic | natural_photo | 100.0% | 0.0% | 100.0% | 95.7% |
| infographic | medical | 100.0% | 0.0% | 100.0% | 96.0% |
| infographic | document | 100.0% | 0.0% | 100.0% | 93.1% |
| infographic | infographic | 100.0% | 0.0% | 100.0% | 84.5% |
| infographic | diagram | 100.0% | 0.0% | 100.0% | 94.6% |
| infographic | chart | 100.0% | 0.0% | 100.0% | 95.6% |
| diagram | natural_photo | 100.0% | 0.0% | 100.0% | 94.4% |
| diagram | medical | 100.0% | 0.0% | 100.0% | 96.7% |
| diagram | document | 100.0% | 0.0% | 100.0% | 94.5% |
| diagram | infographic | 100.0% | 0.0% | 100.0% | 88.0% |
| diagram | diagram | 100.0% | 0.0% | 100.0% | 94.9% |
| diagram | chart | 100.0% | 0.0% | 100.0% | 95.3% |
| chart | natural_photo | 100.0% | 0.0% | 100.0% | 96.4% |
| chart | medical | 100.0% | 0.0% | 100.0% | 97.6% |
| chart | document | 100.0% | 0.0% | 100.0% | 95.2% |
| chart | infographic | 100.0% | 0.0% | 100.0% | 90.2% |
| chart | diagram | 100.0% | 0.0% | 100.0% | 96.7% |
| chart | chart | 100.0% | 0.0% | 100.0% | 94.6% |
