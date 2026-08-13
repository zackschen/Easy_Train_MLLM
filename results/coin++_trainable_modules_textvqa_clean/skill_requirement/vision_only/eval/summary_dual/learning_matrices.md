# CoIN++ Skill Requirement Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.2448 | 0.1602 | 0.1770 | 0.0041 | 0.0753 |
| LLM Judge | 0.2813 | 0.2756 | 0.2699 | 0.0081 | 0.0127 |

## Standard Score Matrix

| Trained until | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recognition | 0.0883 | 0.0337 | 0.0470 | 0.0489 | 0.0138 | 0.0143 | 0.0405 | 0.0290 | 0.0350 | 0.0748 |
| counting | 0.1148 | 0.0612 | 0.0930 | 0.0703 | 0.0518 | 0.0472 | 0.0563 | 0.0396 | 0.0480 | 0.0898 |
| medical_reasoning | 0.1408 | 0.0859 | 0.1670 | 0.0861 | 0.0574 | 0.0610 | 0.0731 | 0.0474 | 0.0693 | 0.1042 |
| knowledge_reasoning | 0.1857 | 0.1498 | 0.1950 | 0.1285 | 0.0544 | 0.0737 | 0.1098 | 0.0552 | 0.1046 | 0.1695 |
| chart_reasoning | 0.2031 | 0.1415 | 0.1920 | 0.1241 | 0.1470 | 0.1031 | 0.1265 | 0.0666 | 0.1104 | 0.1805 |
| document_reasoning | 0.1615 | 0.1199 | 0.1850 | 0.1143 | 0.1489 | 0.1063 | 0.1106 | 0.0664 | 0.0883 | 0.1435 |
| text_reading | 0.2431 | 0.1902 | 0.2030 | 0.1450 | 0.1592 | 0.1275 | 0.2007 | 0.0763 | 0.1588 | 0.2836 |
| diagram_reasoning | 0.2940 | 0.1962 | 0.2040 | 0.2065 | 0.1452 | 0.1456 | 0.2250 | 0.0927 | 0.2024 | 0.3325 |
| relation | 0.3617 | 0.2065 | 0.1760 | 0.2488 | 0.1351 | 0.1441 | 0.2409 | 0.0925 | 0.3199 | 0.4177 |
| attribute | 0.3583 | 0.2064 | 0.1880 | 0.2542 | 0.1423 | 0.1477 | 0.2635 | 0.0959 | 0.3330 | 0.4587 |

## LLM-Judge Score Matrix

| Trained until | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recognition | 0.3589 | 0.1368 | 0.2396 | 0.3036 | 0.0304 | 0.0616 | 0.2247 | 0.0987 | 0.3414 | 0.4420 |
| counting | 0.3925 | 0.1615 | 0.2625 | 0.3049 | 0.0662 | 0.0953 | 0.2445 | 0.1141 | 0.3539 | 0.4702 |
| medical_reasoning | 0.3914 | 0.1770 | 0.2665 | 0.3320 | 0.0598 | 0.0865 | 0.2411 | 0.1034 | 0.3570 | 0.4595 |
| knowledge_reasoning | 0.3970 | 0.2010 | 0.2710 | 0.3422 | 0.0520 | 0.0852 | 0.2383 | 0.1107 | 0.3635 | 0.4501 |
| chart_reasoning | 0.4129 | 0.1931 | 0.2634 | 0.3380 | 0.1367 | 0.1083 | 0.2628 | 0.1094 | 0.3593 | 0.4552 |
| document_reasoning | 0.4055 | 0.1976 | 0.2696 | 0.3659 | 0.1371 | 0.1147 | 0.2823 | 0.1197 | 0.3805 | 0.4705 |
| text_reading | 0.4182 | 0.2211 | 0.2561 | 0.3483 | 0.1401 | 0.1167 | 0.2919 | 0.1207 | 0.3652 | 0.4784 |
| diagram_reasoning | 0.4158 | 0.2197 | 0.2567 | 0.3689 | 0.1263 | 0.1264 | 0.2915 | 0.1194 | 0.3866 | 0.4680 |
| relation | 0.4072 | 0.2095 | 0.2286 | 0.3485 | 0.1229 | 0.1154 | 0.2781 | 0.1073 | 0.3795 | 0.4839 |
| attribute | 0.4098 | 0.2139 | 0.2405 | 0.3624 | 0.1266 | 0.1200 | 0.2958 | 0.1190 | 0.3974 | 0.5275 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| recognition | 0.0883 | 0.3617 | 0.3583 | 0.0034 | 0.2700 |
| counting | 0.0612 | 0.2065 | 0.2064 | 0.0001 | 0.1452 |
| medical_reasoning | 0.1670 | 0.2040 | 0.1880 | 0.0160 | 0.0210 |
| knowledge_reasoning | 0.1285 | 0.2542 | 0.2542 | 0.0000 | 0.1257 |
| chart_reasoning | 0.1470 | 0.1592 | 0.1423 | 0.0170 | -0.0048 |
| document_reasoning | 0.1063 | 0.1477 | 0.1477 | 0.0000 | 0.0414 |
| text_reading | 0.2007 | 0.2635 | 0.2635 | 0.0000 | 0.0628 |
| diagram_reasoning | 0.0927 | 0.0959 | 0.0959 | 0.0000 | 0.0032 |
| relation | 0.3199 | 0.3330 | 0.3330 | 0.0000 | 0.0131 |
| attribute | 0.4587 | 0.4587 | 0.4587 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| recognition | 0.3589 | 0.4182 | 0.4098 | 0.0084 | 0.0509 |
| counting | 0.1615 | 0.2211 | 0.2139 | 0.0072 | 0.0524 |
| medical_reasoning | 0.2665 | 0.2710 | 0.2405 | 0.0305 | -0.0260 |
| knowledge_reasoning | 0.3422 | 0.3689 | 0.3624 | 0.0065 | 0.0202 |
| chart_reasoning | 0.1367 | 0.1401 | 0.1266 | 0.0135 | -0.0101 |
| document_reasoning | 0.1147 | 0.1264 | 0.1200 | 0.0064 | 0.0053 |
| text_reading | 0.2919 | 0.2958 | 0.2958 | 0.0000 | 0.0039 |
| diagram_reasoning | 0.1194 | 0.1194 | 0.1190 | 0.0004 | -0.0004 |
| relation | 0.3795 | 0.3974 | 0.3974 | 0.0000 | 0.0179 |
| attribute | 0.5275 | 0.5275 | 0.5275 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| recognition | recognition | 100.0% | 0.0% | 100.0% | 66.8% |
| recognition | counting | 100.0% | 0.0% | 100.0% | 88.1% |
| recognition | medical_reasoning | 100.0% | 0.0% | 100.0% | 79.2% |
| recognition | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 71.8% |
| recognition | chart_reasoning | 100.0% | 0.0% | 100.0% | 96.2% |
| recognition | document_reasoning | 100.0% | 0.0% | 100.0% | 92.1% |
| recognition | text_reading | 100.0% | 0.0% | 100.0% | 78.9% |
| recognition | diagram_reasoning | 100.0% | 0.0% | 100.0% | 88.7% |
| recognition | relation | 100.0% | 0.0% | 100.0% | 68.5% |
| recognition | attribute | 100.0% | 0.0% | 100.0% | 59.1% |
| counting | recognition | 100.0% | 0.0% | 100.0% | 66.5% |
| counting | counting | 100.0% | 0.0% | 100.0% | 88.7% |
| counting | medical_reasoning | 100.0% | 0.0% | 100.0% | 81.3% |
| counting | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 73.7% |
| counting | chart_reasoning | 100.0% | 0.0% | 100.0% | 92.2% |
| counting | document_reasoning | 100.0% | 0.0% | 100.0% | 88.3% |
| counting | text_reading | 100.0% | 0.0% | 100.0% | 77.8% |
| counting | diagram_reasoning | 100.0% | 0.0% | 100.0% | 88.1% |
| counting | relation | 100.0% | 0.0% | 100.0% | 68.5% |
| counting | attribute | 100.0% | 0.0% | 100.0% | 57.9% |
| medical_reasoning | recognition | 100.0% | 0.0% | 100.0% | 69.2% |
| medical_reasoning | counting | 100.0% | 0.0% | 100.0% | 89.6% |
| medical_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 88.5% |
| medical_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 72.2% |
| medical_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 92.4% |
| medical_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 87.8% |
| medical_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 79.6% |
| medical_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 89.6% |
| medical_reasoning | relation | 100.0% | 0.0% | 100.0% | 70.3% |
| medical_reasoning | attribute | 100.0% | 0.0% | 100.0% | 60.7% |
| knowledge_reasoning | recognition | 100.0% | 0.0% | 100.0% | 72.7% |
| knowledge_reasoning | counting | 100.0% | 0.0% | 100.0% | 93.5% |
| knowledge_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 90.9% |
| knowledge_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 75.1% |
| knowledge_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.8% |
| knowledge_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 87.5% |
| knowledge_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 82.7% |
| knowledge_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 89.8% |
| knowledge_reasoning | relation | 100.0% | 0.0% | 100.0% | 73.1% |
| knowledge_reasoning | attribute | 100.0% | 0.0% | 100.0% | 67.8% |
| chart_reasoning | recognition | 100.0% | 0.0% | 100.0% | 72.2% |
| chart_reasoning | counting | 100.0% | 0.0% | 100.0% | 93.5% |
| chart_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 91.4% |
| chart_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 75.1% |
| chart_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 92.6% |
| chart_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 84.0% |
| chart_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 80.3% |
| chart_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 90.7% |
| chart_reasoning | relation | 100.0% | 0.0% | 100.0% | 74.0% |
| chart_reasoning | attribute | 100.0% | 0.0% | 100.0% | 69.0% |
| document_reasoning | recognition | 100.0% | 0.0% | 100.0% | 69.5% |
| document_reasoning | counting | 100.0% | 0.0% | 100.0% | 91.2% |
| document_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 90.1% |
| document_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 71.9% |
| document_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 91.3% |
| document_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 83.9% |
| document_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 77.8% |
| document_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 89.9% |
| document_reasoning | relation | 100.0% | 0.0% | 100.0% | 69.9% |
| document_reasoning | attribute | 100.0% | 0.0% | 100.0% | 63.8% |
| text_reading | recognition | 100.0% | 0.0% | 100.0% | 75.7% |
| text_reading | counting | 100.0% | 0.0% | 100.0% | 95.4% |
| text_reading | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.7% |
| text_reading | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 76.2% |
| text_reading | chart_reasoning | 100.0% | 0.0% | 100.0% | 91.8% |
| text_reading | document_reasoning | 100.0% | 0.0% | 100.0% | 82.7% |
| text_reading | text_reading | 100.0% | 0.0% | 100.0% | 83.8% |
| text_reading | diagram_reasoning | 100.0% | 0.0% | 100.0% | 91.2% |
| text_reading | relation | 100.0% | 0.0% | 100.0% | 78.2% |
| text_reading | attribute | 100.0% | 0.0% | 100.0% | 77.6% |
| diagram_reasoning | recognition | 100.0% | 0.0% | 100.0% | 80.7% |
| diagram_reasoning | counting | 100.0% | 0.0% | 100.0% | 96.2% |
| diagram_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.5% |
| diagram_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 80.4% |
| diagram_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.6% |
| diagram_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 82.2% |
| diagram_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 85.0% |
| diagram_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.7% |
| diagram_reasoning | relation | 100.0% | 0.0% | 100.0% | 80.1% |
| diagram_reasoning | attribute | 100.0% | 0.0% | 100.0% | 83.1% |
| relation | recognition | 100.0% | 0.0% | 100.0% | 88.7% |
| relation | counting | 100.0% | 0.0% | 100.0% | 96.8% |
| relation | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.6% |
| relation | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 85.9% |
| relation | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.7% |
| relation | document_reasoning | 100.0% | 0.0% | 100.0% | 85.1% |
| relation | text_reading | 100.0% | 0.0% | 100.0% | 91.0% |
| relation | diagram_reasoning | 100.0% | 0.0% | 100.0% | 94.7% |
| relation | relation | 100.0% | 0.0% | 100.0% | 92.4% |
| relation | attribute | 100.0% | 0.0% | 100.0% | 90.6% |
| attribute | recognition | 100.0% | 0.0% | 100.0% | 88.3% |
| attribute | counting | 100.0% | 0.0% | 100.0% | 97.5% |
| attribute | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.7% |
| attribute | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 84.7% |
| attribute | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.1% |
| attribute | document_reasoning | 100.0% | 0.0% | 100.0% | 84.9% |
| attribute | text_reading | 100.0% | 0.0% | 100.0% | 89.4% |
| attribute | diagram_reasoning | 100.0% | 0.0% | 100.0% | 93.4% |
| attribute | relation | 100.0% | 0.0% | 100.0% | 91.7% |
| attribute | attribute | 100.0% | 0.0% | 100.0% | 90.2% |
