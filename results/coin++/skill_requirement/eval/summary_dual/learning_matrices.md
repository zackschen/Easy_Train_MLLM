# CoIN++ Skill Requirement Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.2243 | 0.2754 | 0.2939 | 0.0773 | -0.0773 |
| LLM Judge | 0.2338 | 0.2981 | 0.3098 | 0.0847 | -0.0845 |

## Standard Score Matrix

| Trained until | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recognition | 0.5553 | 0.0970 | 0.2720 | 0.3468 | 0.1278 | 0.1624 | 0.2507 | 0.1691 | 0.3896 | 0.4101 |
| counting | 0.2551 | 0.2545 | 0.1940 | 0.2261 | 0.0648 | 0.0646 | 0.0734 | 0.1131 | 0.2651 | 0.3202 |
| medical_reasoning | 0.2726 | 0.2249 | 0.3680 | 0.2813 | 0.0969 | 0.0967 | 0.0976 | 0.1490 | 0.2560 | 0.3009 |
| knowledge_reasoning | 0.2703 | 0.2127 | 0.3370 | 0.3463 | 0.1133 | 0.0997 | 0.1175 | 0.1622 | 0.2730 | 0.3543 |
| chart_reasoning | 0.2220 | 0.2141 | 0.3400 | 0.3297 | 0.1858 | 0.1106 | 0.1319 | 0.0985 | 0.2431 | 0.2890 |
| document_reasoning | 0.2276 | 0.2367 | 0.3430 | 0.3035 | 0.1613 | 0.1535 | 0.1196 | 0.1114 | 0.2180 | 0.2892 |
| text_reading | 0.2485 | 0.1633 | 0.2950 | 0.3204 | 0.1434 | 0.1476 | 0.1476 | 0.1435 | 0.2514 | 0.3252 |
| diagram_reasoning | 0.2688 | 0.2248 | 0.3500 | 0.3231 | 0.1277 | 0.1289 | 0.1437 | 0.2172 | 0.2482 | 0.3409 |
| relation | 0.2575 | 0.2044 | 0.2840 | 0.2896 | 0.1113 | 0.1177 | 0.1274 | 0.1748 | 0.3319 | 0.3310 |
| attribute | 0.2667 | 0.2190 | 0.3000 | 0.2910 | 0.1181 | 0.1002 | 0.1058 | 0.1659 | 0.2973 | 0.3790 |

## LLM-Judge Score Matrix

| Trained until | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recognition | 0.6145 | 0.0970 | 0.3226 | 0.4746 | 0.1081 | 0.1402 | 0.2869 | 0.2156 | 0.4484 | 0.4295 |
| counting | 0.2745 | 0.2561 | 0.2140 | 0.2954 | 0.0688 | 0.0539 | 0.0831 | 0.1534 | 0.2932 | 0.3329 |
| medical_reasoning | 0.2966 | 0.2340 | 0.4145 | 0.3725 | 0.0832 | 0.0719 | 0.1180 | 0.2101 | 0.2945 | 0.3204 |
| knowledge_reasoning | 0.2976 | 0.2160 | 0.3664 | 0.4268 | 0.0933 | 0.0854 | 0.1266 | 0.1999 | 0.2966 | 0.3851 |
| chart_reasoning | 0.2471 | 0.2128 | 0.3704 | 0.4172 | 0.1557 | 0.0832 | 0.1332 | 0.1364 | 0.2681 | 0.3217 |
| document_reasoning | 0.2577 | 0.2429 | 0.3866 | 0.4063 | 0.1460 | 0.1023 | 0.1302 | 0.1600 | 0.2535 | 0.3297 |
| text_reading | 0.2756 | 0.1707 | 0.3291 | 0.4055 | 0.1217 | 0.1043 | 0.1528 | 0.1909 | 0.2750 | 0.3563 |
| diagram_reasoning | 0.2981 | 0.2281 | 0.3807 | 0.4029 | 0.1084 | 0.0848 | 0.1514 | 0.2502 | 0.2601 | 0.3663 |
| relation | 0.2790 | 0.2021 | 0.3298 | 0.3804 | 0.0920 | 0.0794 | 0.1356 | 0.1956 | 0.3549 | 0.3572 |
| attribute | 0.2793 | 0.1931 | 0.3377 | 0.3527 | 0.1029 | 0.0722 | 0.1252 | 0.1917 | 0.3124 | 0.3706 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| recognition | 0.5553 | 0.5553 | 0.2667 | 0.2886 | -0.2886 |
| counting | 0.2545 | 0.2545 | 0.2190 | 0.0355 | -0.0355 |
| medical_reasoning | 0.3680 | 0.3680 | 0.3000 | 0.0680 | -0.0680 |
| knowledge_reasoning | 0.3463 | 0.3463 | 0.2910 | 0.0553 | -0.0553 |
| chart_reasoning | 0.1858 | 0.1858 | 0.1181 | 0.0677 | -0.0677 |
| document_reasoning | 0.1535 | 0.1535 | 0.1002 | 0.0533 | -0.0533 |
| text_reading | 0.1476 | 0.1476 | 0.1058 | 0.0418 | -0.0418 |
| diagram_reasoning | 0.2172 | 0.2172 | 0.1659 | 0.0513 | -0.0513 |
| relation | 0.3319 | 0.3319 | 0.2973 | 0.0346 | -0.0346 |
| attribute | 0.3790 | 0.3790 | 0.3790 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| recognition | 0.6145 | 0.6145 | 0.2793 | 0.3352 | -0.3352 |
| counting | 0.2561 | 0.2561 | 0.1931 | 0.0630 | -0.0630 |
| medical_reasoning | 0.4145 | 0.4145 | 0.3377 | 0.0767 | -0.0767 |
| knowledge_reasoning | 0.4268 | 0.4268 | 0.3527 | 0.0741 | -0.0741 |
| chart_reasoning | 0.1557 | 0.1557 | 0.1029 | 0.0528 | -0.0528 |
| document_reasoning | 0.1023 | 0.1043 | 0.0722 | 0.0321 | -0.0301 |
| text_reading | 0.1528 | 0.1528 | 0.1252 | 0.0276 | -0.0276 |
| diagram_reasoning | 0.2502 | 0.2502 | 0.1917 | 0.0585 | -0.0585 |
| relation | 0.3549 | 0.3549 | 0.3124 | 0.0425 | -0.0425 |
| attribute | 0.3706 | 0.3706 | 0.3706 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| recognition | recognition | 100.0% | 0.0% | 100.0% | 91.6% |
| recognition | counting | 100.0% | 0.0% | 100.0% | 99.3% |
| recognition | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.4% |
| recognition | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 83.3% |
| recognition | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.1% |
| recognition | document_reasoning | 100.0% | 0.0% | 100.0% | 84.7% |
| recognition | text_reading | 100.0% | 0.0% | 100.0% | 89.4% |
| recognition | diagram_reasoning | 100.0% | 0.0% | 100.0% | 94.5% |
| recognition | relation | 100.0% | 0.0% | 100.0% | 92.6% |
| recognition | attribute | 100.0% | 0.0% | 100.0% | 93.8% |
| counting | recognition | 100.0% | 0.0% | 100.0% | 95.1% |
| counting | counting | 100.0% | 0.0% | 100.0% | 97.7% |
| counting | medical_reasoning | 100.0% | 0.0% | 100.0% | 96.2% |
| counting | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 90.3% |
| counting | chart_reasoning | 100.0% | 0.0% | 100.0% | 97.3% |
| counting | document_reasoning | 100.0% | 0.0% | 100.0% | 92.4% |
| counting | text_reading | 100.0% | 0.0% | 100.0% | 98.2% |
| counting | diagram_reasoning | 100.0% | 0.0% | 100.0% | 94.9% |
| counting | relation | 100.0% | 0.0% | 100.0% | 96.0% |
| counting | attribute | 100.0% | 0.0% | 100.0% | 94.4% |
| medical_reasoning | recognition | 100.0% | 0.0% | 100.0% | 95.7% |
| medical_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.0% |
| medical_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 94.2% |
| medical_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 87.6% |
| medical_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.5% |
| medical_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 87.7% |
| medical_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 94.9% |
| medical_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.8% |
| medical_reasoning | relation | 100.0% | 0.0% | 100.0% | 93.9% |
| medical_reasoning | attribute | 100.0% | 0.0% | 100.0% | 97.0% |
| knowledge_reasoning | recognition | 100.0% | 0.0% | 100.0% | 95.6% |
| knowledge_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.2% |
| knowledge_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 95.4% |
| knowledge_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 89.6% |
| knowledge_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.9% |
| knowledge_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 89.5% |
| knowledge_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 94.8% |
| knowledge_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 93.6% |
| knowledge_reasoning | relation | 100.0% | 0.0% | 100.0% | 96.1% |
| knowledge_reasoning | attribute | 100.0% | 0.0% | 100.0% | 96.3% |
| chart_reasoning | recognition | 100.0% | 0.0% | 100.0% | 95.6% |
| chart_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.5% |
| chart_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 95.3% |
| chart_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 88.2% |
| chart_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.5% |
| chart_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 87.2% |
| chart_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 95.1% |
| chart_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 93.9% |
| chart_reasoning | relation | 100.0% | 0.0% | 100.0% | 96.3% |
| chart_reasoning | attribute | 100.0% | 0.0% | 100.0% | 95.2% |
| document_reasoning | recognition | 100.0% | 0.0% | 100.0% | 94.3% |
| document_reasoning | counting | 100.0% | 0.0% | 100.0% | 96.8% |
| document_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.7% |
| document_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 86.5% |
| document_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.0% |
| document_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 83.8% |
| document_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 94.3% |
| document_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 93.2% |
| document_reasoning | relation | 100.0% | 0.0% | 100.0% | 93.5% |
| document_reasoning | attribute | 100.0% | 0.0% | 100.0% | 94.4% |
| text_reading | recognition | 100.0% | 0.0% | 100.0% | 95.7% |
| text_reading | counting | 100.0% | 0.0% | 100.0% | 97.2% |
| text_reading | medical_reasoning | 100.0% | 0.0% | 100.0% | 95.4% |
| text_reading | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 88.9% |
| text_reading | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.6% |
| text_reading | document_reasoning | 100.0% | 0.0% | 100.0% | 83.7% |
| text_reading | text_reading | 100.0% | 0.0% | 100.0% | 94.0% |
| text_reading | diagram_reasoning | 100.0% | 0.0% | 100.0% | 94.1% |
| text_reading | relation | 100.0% | 0.0% | 100.0% | 96.7% |
| text_reading | attribute | 100.0% | 0.0% | 100.0% | 96.2% |
| diagram_reasoning | recognition | 100.0% | 0.0% | 100.0% | 95.2% |
| diagram_reasoning | counting | 100.0% | 0.0% | 100.0% | 96.5% |
| diagram_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 95.4% |
| diagram_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 88.4% |
| diagram_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.7% |
| diagram_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 85.5% |
| diagram_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 94.5% |
| diagram_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 94.6% |
| diagram_reasoning | relation | 100.0% | 0.0% | 100.0% | 97.3% |
| diagram_reasoning | attribute | 100.0% | 0.0% | 100.0% | 96.6% |
| relation | recognition | 100.0% | 0.0% | 100.0% | 96.3% |
| relation | counting | 100.0% | 0.0% | 100.0% | 97.1% |
| relation | medical_reasoning | 100.0% | 0.0% | 100.0% | 94.4% |
| relation | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 88.9% |
| relation | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.9% |
| relation | document_reasoning | 100.0% | 0.0% | 100.0% | 87.7% |
| relation | text_reading | 100.0% | 0.0% | 100.0% | 93.8% |
| relation | diagram_reasoning | 100.0% | 0.0% | 100.0% | 96.6% |
| relation | relation | 100.0% | 0.0% | 100.0% | 96.5% |
| relation | attribute | 100.0% | 0.0% | 100.0% | 96.9% |
| attribute | recognition | 100.0% | 0.0% | 100.0% | 94.2% |
| attribute | counting | 100.0% | 0.0% | 100.0% | 95.2% |
| attribute | medical_reasoning | 100.0% | 0.0% | 100.0% | 95.2% |
| attribute | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 87.9% |
| attribute | chart_reasoning | 100.0% | 0.0% | 100.0% | 95.9% |
| attribute | document_reasoning | 100.0% | 0.0% | 100.0% | 90.2% |
| attribute | text_reading | 100.0% | 0.0% | 100.0% | 93.8% |
| attribute | diagram_reasoning | 100.0% | 0.0% | 100.0% | 96.7% |
| attribute | relation | 100.0% | 0.0% | 100.0% | 96.9% |
| attribute | attribute | 100.0% | 0.0% | 100.0% | 94.4% |
