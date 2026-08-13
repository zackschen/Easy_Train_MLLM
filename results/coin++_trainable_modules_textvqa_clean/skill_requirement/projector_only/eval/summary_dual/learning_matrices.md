# CoIN++ Skill Requirement Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.2877 | 0.2860 | 0.2867 | 0.0141 | 0.0011 |
| LLM Judge | 0.3234 | 0.3250 | 0.3213 | 0.0086 | 0.0023 |

## Standard Score Matrix

| Trained until | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recognition | 0.3554 | 0.2050 | 0.2070 | 0.2480 | 0.0621 | 0.0946 | 0.2126 | 0.0805 | 0.2804 | 0.3988 |
| counting | 0.3817 | 0.2534 | 0.2200 | 0.2407 | 0.0703 | 0.1134 | 0.2265 | 0.0774 | 0.3020 | 0.3738 |
| medical_reasoning | 0.3832 | 0.2215 | 0.2410 | 0.2583 | 0.0807 | 0.1295 | 0.2341 | 0.0877 | 0.2742 | 0.3951 |
| knowledge_reasoning | 0.4219 | 0.2287 | 0.1940 | 0.3107 | 0.0930 | 0.1474 | 0.2644 | 0.1040 | 0.3545 | 0.4360 |
| chart_reasoning | 0.4331 | 0.2443 | 0.2170 | 0.2970 | 0.1835 | 0.1715 | 0.2838 | 0.1026 | 0.3247 | 0.4199 |
| document_reasoning | 0.4234 | 0.2560 | 0.2140 | 0.2963 | 0.1763 | 0.2071 | 0.2915 | 0.1100 | 0.3451 | 0.4097 |
| text_reading | 0.4271 | 0.2699 | 0.1990 | 0.2980 | 0.1865 | 0.2171 | 0.3211 | 0.1173 | 0.3549 | 0.4306 |
| diagram_reasoning | 0.4275 | 0.2535 | 0.2090 | 0.3254 | 0.1792 | 0.2031 | 0.3215 | 0.1233 | 0.3552 | 0.4237 |
| relation | 0.4369 | 0.2547 | 0.1820 | 0.3060 | 0.1552 | 0.1915 | 0.3219 | 0.1241 | 0.3821 | 0.4573 |
| attribute | 0.4466 | 0.2698 | 0.1920 | 0.3149 | 0.1531 | 0.1929 | 0.3188 | 0.1200 | 0.3796 | 0.4898 |

## LLM-Judge Score Matrix

| Trained until | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recognition | 0.4287 | 0.2134 | 0.2516 | 0.3503 | 0.0493 | 0.0867 | 0.2697 | 0.1014 | 0.3801 | 0.4688 |
| counting | 0.4446 | 0.2658 | 0.2647 | 0.3676 | 0.0793 | 0.1035 | 0.2685 | 0.0977 | 0.3892 | 0.4477 |
| medical_reasoning | 0.4397 | 0.2293 | 0.2875 | 0.3932 | 0.0754 | 0.1091 | 0.2739 | 0.1155 | 0.3661 | 0.4644 |
| knowledge_reasoning | 0.4711 | 0.2361 | 0.2485 | 0.4369 | 0.0863 | 0.1251 | 0.3053 | 0.1338 | 0.4142 | 0.5086 |
| chart_reasoning | 0.4908 | 0.2708 | 0.2678 | 0.4237 | 0.1505 | 0.1426 | 0.3128 | 0.1244 | 0.3984 | 0.4898 |
| document_reasoning | 0.4734 | 0.2626 | 0.2640 | 0.4222 | 0.1515 | 0.1489 | 0.3172 | 0.1346 | 0.4144 | 0.4816 |
| text_reading | 0.4788 | 0.2753 | 0.2548 | 0.4099 | 0.1580 | 0.1562 | 0.3446 | 0.1299 | 0.4222 | 0.4971 |
| diagram_reasoning | 0.4726 | 0.2641 | 0.2686 | 0.4353 | 0.1612 | 0.1499 | 0.3429 | 0.1502 | 0.4177 | 0.4916 |
| relation | 0.4762 | 0.2640 | 0.2384 | 0.4199 | 0.1400 | 0.1419 | 0.3487 | 0.1458 | 0.4399 | 0.5203 |
| attribute | 0.4917 | 0.2778 | 0.2498 | 0.4299 | 0.1370 | 0.1497 | 0.3466 | 0.1506 | 0.4409 | 0.5604 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| recognition | 0.3554 | 0.4466 | 0.4466 | 0.0000 | 0.0912 |
| counting | 0.2534 | 0.2699 | 0.2698 | 0.0001 | 0.0164 |
| medical_reasoning | 0.2410 | 0.2410 | 0.1920 | 0.0490 | -0.0490 |
| knowledge_reasoning | 0.3107 | 0.3254 | 0.3149 | 0.0105 | 0.0042 |
| chart_reasoning | 0.1835 | 0.1865 | 0.1531 | 0.0334 | -0.0304 |
| document_reasoning | 0.2071 | 0.2171 | 0.1929 | 0.0242 | -0.0142 |
| text_reading | 0.3211 | 0.3219 | 0.3188 | 0.0031 | -0.0023 |
| diagram_reasoning | 0.1233 | 0.1241 | 0.1200 | 0.0041 | -0.0033 |
| relation | 0.3821 | 0.3821 | 0.3796 | 0.0025 | -0.0025 |
| attribute | 0.4898 | 0.4898 | 0.4898 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| recognition | 0.4287 | 0.4917 | 0.4917 | 0.0000 | 0.0630 |
| counting | 0.2658 | 0.2778 | 0.2778 | 0.0000 | 0.0120 |
| medical_reasoning | 0.2875 | 0.2875 | 0.2498 | 0.0377 | -0.0377 |
| knowledge_reasoning | 0.4369 | 0.4369 | 0.4299 | 0.0070 | -0.0070 |
| chart_reasoning | 0.1505 | 0.1612 | 0.1370 | 0.0242 | -0.0135 |
| document_reasoning | 0.1489 | 0.1562 | 0.1497 | 0.0065 | 0.0008 |
| text_reading | 0.3446 | 0.3487 | 0.3466 | 0.0021 | 0.0020 |
| diagram_reasoning | 0.1502 | 0.1506 | 0.1506 | 0.0000 | 0.0004 |
| relation | 0.4399 | 0.4409 | 0.4409 | 0.0000 | 0.0010 |
| attribute | 0.5604 | 0.5604 | 0.5604 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| recognition | recognition | 100.0% | 0.0% | 100.0% | 85.9% |
| recognition | counting | 100.0% | 0.0% | 100.0% | 96.7% |
| recognition | medical_reasoning | 100.0% | 0.0% | 100.0% | 94.4% |
| recognition | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 84.4% |
| recognition | chart_reasoning | 100.0% | 0.0% | 100.0% | 95.5% |
| recognition | document_reasoning | 100.0% | 0.0% | 100.0% | 88.3% |
| recognition | text_reading | 100.0% | 0.0% | 100.0% | 90.1% |
| recognition | diagram_reasoning | 100.0% | 0.0% | 100.0% | 91.6% |
| recognition | relation | 100.0% | 0.0% | 100.0% | 88.1% |
| recognition | attribute | 100.0% | 0.0% | 100.0% | 89.7% |
| counting | recognition | 100.0% | 0.0% | 100.0% | 86.8% |
| counting | counting | 100.0% | 0.0% | 100.0% | 96.3% |
| counting | medical_reasoning | 100.0% | 0.0% | 100.0% | 94.5% |
| counting | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 81.4% |
| counting | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.9% |
| counting | document_reasoning | 100.0% | 0.0% | 100.0% | 85.9% |
| counting | text_reading | 100.0% | 0.0% | 100.0% | 88.3% |
| counting | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.5% |
| counting | relation | 100.0% | 0.0% | 100.0% | 88.6% |
| counting | attribute | 100.0% | 0.0% | 100.0% | 89.5% |
| medical_reasoning | recognition | 100.0% | 0.0% | 100.0% | 86.6% |
| medical_reasoning | counting | 100.0% | 0.0% | 100.0% | 96.6% |
| medical_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 94.3% |
| medical_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 81.2% |
| medical_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 95.0% |
| medical_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 85.2% |
| medical_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 89.2% |
| medical_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 91.4% |
| medical_reasoning | relation | 100.0% | 0.0% | 100.0% | 88.3% |
| medical_reasoning | attribute | 100.0% | 0.0% | 100.0% | 89.7% |
| knowledge_reasoning | recognition | 100.0% | 0.0% | 100.0% | 88.5% |
| knowledge_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.3% |
| knowledge_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.4% |
| knowledge_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 83.8% |
| knowledge_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 95.9% |
| knowledge_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 83.8% |
| knowledge_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 90.6% |
| knowledge_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.9% |
| knowledge_reasoning | relation | 100.0% | 0.0% | 100.0% | 92.6% |
| knowledge_reasoning | attribute | 100.0% | 0.0% | 100.0% | 89.5% |
| chart_reasoning | recognition | 100.0% | 0.0% | 100.0% | 87.2% |
| chart_reasoning | counting | 100.0% | 0.0% | 100.0% | 96.3% |
| chart_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 94.0% |
| chart_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 83.5% |
| chart_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.7% |
| chart_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 83.1% |
| chart_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 89.7% |
| chart_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 93.2% |
| chart_reasoning | relation | 100.0% | 0.0% | 100.0% | 90.8% |
| chart_reasoning | attribute | 100.0% | 0.0% | 100.0% | 89.1% |
| document_reasoning | recognition | 100.0% | 0.0% | 100.0% | 87.3% |
| document_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.7% |
| document_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 94.0% |
| document_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 82.5% |
| document_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.2% |
| document_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 80.5% |
| document_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 87.2% |
| document_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.6% |
| document_reasoning | relation | 100.0% | 0.0% | 100.0% | 90.8% |
| document_reasoning | attribute | 100.0% | 0.0% | 100.0% | 89.5% |
| text_reading | recognition | 100.0% | 0.0% | 100.0% | 87.4% |
| text_reading | counting | 100.0% | 0.0% | 100.0% | 97.7% |
| text_reading | medical_reasoning | 100.0% | 0.0% | 100.0% | 92.9% |
| text_reading | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 84.3% |
| text_reading | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.8% |
| text_reading | document_reasoning | 100.0% | 0.0% | 100.0% | 80.7% |
| text_reading | text_reading | 100.0% | 0.0% | 100.0% | 87.8% |
| text_reading | diagram_reasoning | 100.0% | 0.0% | 100.0% | 93.1% |
| text_reading | relation | 100.0% | 0.0% | 100.0% | 91.3% |
| text_reading | attribute | 100.0% | 0.0% | 100.0% | 90.0% |
| diagram_reasoning | recognition | 100.0% | 0.0% | 100.0% | 88.3% |
| diagram_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.3% |
| diagram_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 92.9% |
| diagram_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 84.8% |
| diagram_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.9% |
| diagram_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 81.6% |
| diagram_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 88.3% |
| diagram_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.3% |
| diagram_reasoning | relation | 100.0% | 0.0% | 100.0% | 91.9% |
| diagram_reasoning | attribute | 100.0% | 0.0% | 100.0% | 89.6% |
| relation | recognition | 100.0% | 0.0% | 100.0% | 89.4% |
| relation | counting | 100.0% | 0.0% | 100.0% | 97.2% |
| relation | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.1% |
| relation | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 84.5% |
| relation | chart_reasoning | 100.0% | 0.0% | 100.0% | 95.2% |
| relation | document_reasoning | 100.0% | 0.0% | 100.0% | 82.7% |
| relation | text_reading | 100.0% | 0.0% | 100.0% | 87.4% |
| relation | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.8% |
| relation | relation | 100.0% | 0.0% | 100.0% | 92.4% |
| relation | attribute | 100.0% | 0.0% | 100.0% | 90.5% |
| attribute | recognition | 100.0% | 0.0% | 100.0% | 88.4% |
| attribute | counting | 100.0% | 0.0% | 100.0% | 97.4% |
| attribute | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.0% |
| attribute | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 83.9% |
| attribute | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.6% |
| attribute | document_reasoning | 100.0% | 0.0% | 100.0% | 81.7% |
| attribute | text_reading | 100.0% | 0.0% | 100.0% | 87.5% |
| attribute | diagram_reasoning | 100.0% | 0.0% | 100.0% | 91.7% |
| attribute | relation | 100.0% | 0.0% | 100.0% | 92.1% |
| attribute | attribute | 100.0% | 0.0% | 100.0% | 89.7% |
