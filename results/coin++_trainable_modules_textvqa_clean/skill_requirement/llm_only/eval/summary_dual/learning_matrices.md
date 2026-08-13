# CoIN++ Skill Requirement Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.3183 | 0.3924 | 0.3853 | 0.0757 | -0.0745 |
| LLM Judge | 0.3455 | 0.4273 | 0.4082 | 0.0714 | -0.0697 |

## Standard Score Matrix

| Trained until | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recognition | 0.5562 | 0.2156 | 0.2870 | 0.3536 | 0.1422 | 0.1781 | 0.2966 | 0.1641 | 0.3904 | 0.4688 |
| counting | 0.5244 | 0.3527 | 0.2680 | 0.3414 | 0.1246 | 0.1073 | 0.2393 | 0.1304 | 0.3699 | 0.4491 |
| medical_reasoning | 0.5108 | 0.3497 | 0.3910 | 0.3402 | 0.1270 | 0.1647 | 0.2772 | 0.1675 | 0.3579 | 0.4527 |
| knowledge_reasoning | 0.5272 | 0.3361 | 0.3930 | 0.4367 | 0.1467 | 0.1454 | 0.2468 | 0.1933 | 0.3729 | 0.4336 |
| chart_reasoning | 0.5363 | 0.3431 | 0.3850 | 0.4227 | 0.2738 | 0.1709 | 0.3058 | 0.1986 | 0.3647 | 0.4323 |
| document_reasoning | 0.4963 | 0.3520 | 0.3900 | 0.4048 | 0.2828 | 0.2753 | 0.3217 | 0.1768 | 0.3593 | 0.4212 |
| text_reading | 0.5284 | 0.3246 | 0.3890 | 0.4220 | 0.2757 | 0.2732 | 0.3863 | 0.1708 | 0.3897 | 0.4285 |
| diagram_reasoning | 0.5230 | 0.3171 | 0.3780 | 0.4236 | 0.2786 | 0.2368 | 0.3815 | 0.2160 | 0.3897 | 0.4128 |
| relation | 0.4526 | 0.1831 | 0.3280 | 0.3422 | 0.1701 | 0.2270 | 0.3323 | 0.1892 | 0.4365 | 0.4419 |
| attribute | 0.4465 | 0.2110 | 0.3360 | 0.3581 | 0.1963 | 0.1963 | 0.2980 | 0.2115 | 0.4007 | 0.5289 |

## LLM-Judge Score Matrix

| Trained until | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recognition | 0.6175 | 0.2186 | 0.3420 | 0.4752 | 0.1226 | 0.1510 | 0.3291 | 0.2103 | 0.4383 | 0.5152 |
| counting | 0.5833 | 0.3604 | 0.3067 | 0.4501 | 0.1209 | 0.1070 | 0.2911 | 0.1883 | 0.4262 | 0.4844 |
| medical_reasoning | 0.5829 | 0.3531 | 0.4507 | 0.4777 | 0.1209 | 0.1275 | 0.3117 | 0.2192 | 0.4190 | 0.5037 |
| knowledge_reasoning | 0.5935 | 0.3406 | 0.4411 | 0.5307 | 0.1230 | 0.1274 | 0.2836 | 0.2325 | 0.4092 | 0.4832 |
| chart_reasoning | 0.6061 | 0.3472 | 0.4401 | 0.5157 | 0.2408 | 0.1329 | 0.3190 | 0.2336 | 0.4041 | 0.4797 |
| document_reasoning | 0.5751 | 0.3609 | 0.4451 | 0.5128 | 0.2432 | 0.1882 | 0.3357 | 0.2138 | 0.4040 | 0.4710 |
| text_reading | 0.5841 | 0.3259 | 0.4472 | 0.5374 | 0.2426 | 0.1900 | 0.3977 | 0.2017 | 0.4196 | 0.4698 |
| diagram_reasoning | 0.5791 | 0.3214 | 0.4026 | 0.5202 | 0.2471 | 0.1740 | 0.3830 | 0.2528 | 0.4310 | 0.4593 |
| relation | 0.5211 | 0.2120 | 0.3818 | 0.4446 | 0.2121 | 0.1702 | 0.3474 | 0.2240 | 0.4789 | 0.4852 |
| attribute | 0.5105 | 0.2281 | 0.3709 | 0.4546 | 0.1829 | 0.1458 | 0.3080 | 0.2441 | 0.4456 | 0.5645 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| recognition | 0.5562 | 0.5562 | 0.4465 | 0.1097 | -0.1097 |
| counting | 0.3527 | 0.3527 | 0.2110 | 0.1417 | -0.1417 |
| medical_reasoning | 0.3910 | 0.3930 | 0.3360 | 0.0570 | -0.0550 |
| knowledge_reasoning | 0.4367 | 0.4367 | 0.3581 | 0.0786 | -0.0786 |
| chart_reasoning | 0.2738 | 0.2828 | 0.1963 | 0.0865 | -0.0775 |
| document_reasoning | 0.2753 | 0.2753 | 0.1963 | 0.0791 | -0.0791 |
| text_reading | 0.3863 | 0.3863 | 0.2980 | 0.0882 | -0.0882 |
| diagram_reasoning | 0.2160 | 0.2160 | 0.2115 | 0.0045 | -0.0045 |
| relation | 0.4365 | 0.4365 | 0.4007 | 0.0359 | -0.0359 |
| attribute | 0.5289 | 0.5289 | 0.5289 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| recognition | 0.6175 | 0.6175 | 0.5105 | 0.1070 | -0.1070 |
| counting | 0.3604 | 0.3609 | 0.2281 | 0.1328 | -0.1323 |
| medical_reasoning | 0.4507 | 0.4507 | 0.3709 | 0.0798 | -0.0798 |
| knowledge_reasoning | 0.5307 | 0.5374 | 0.4546 | 0.0828 | -0.0761 |
| chart_reasoning | 0.2408 | 0.2471 | 0.1829 | 0.0642 | -0.0579 |
| document_reasoning | 0.1882 | 0.1900 | 0.1458 | 0.0442 | -0.0424 |
| text_reading | 0.3977 | 0.3977 | 0.3080 | 0.0897 | -0.0897 |
| diagram_reasoning | 0.2528 | 0.2528 | 0.2441 | 0.0087 | -0.0087 |
| relation | 0.4789 | 0.4789 | 0.4456 | 0.0333 | -0.0333 |
| attribute | 0.5645 | 0.5645 | 0.5645 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| recognition | recognition | 100.0% | 0.0% | 100.0% | 92.3% |
| recognition | counting | 100.0% | 0.0% | 100.0% | 97.3% |
| recognition | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.1% |
| recognition | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 84.1% |
| recognition | chart_reasoning | 100.0% | 0.0% | 100.0% | 92.9% |
| recognition | document_reasoning | 100.0% | 0.0% | 100.0% | 83.4% |
| recognition | text_reading | 100.0% | 0.0% | 100.0% | 89.4% |
| recognition | diagram_reasoning | 100.0% | 0.0% | 100.0% | 93.2% |
| recognition | relation | 100.0% | 0.0% | 100.0% | 93.5% |
| recognition | attribute | 100.0% | 0.0% | 100.0% | 95.2% |
| counting | recognition | 100.0% | 0.0% | 100.0% | 92.2% |
| counting | counting | 100.0% | 0.0% | 100.0% | 97.6% |
| counting | medical_reasoning | 100.0% | 0.0% | 100.0% | 95.0% |
| counting | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 85.9% |
| counting | chart_reasoning | 100.0% | 0.0% | 100.0% | 96.8% |
| counting | document_reasoning | 100.0% | 0.0% | 100.0% | 90.4% |
| counting | text_reading | 100.0% | 0.0% | 100.0% | 90.5% |
| counting | diagram_reasoning | 100.0% | 0.0% | 100.0% | 93.8% |
| counting | relation | 100.0% | 0.0% | 100.0% | 93.3% |
| counting | attribute | 100.0% | 0.0% | 100.0% | 95.9% |
| medical_reasoning | recognition | 100.0% | 0.0% | 100.0% | 89.9% |
| medical_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.1% |
| medical_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 92.7% |
| medical_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 81.3% |
| medical_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.1% |
| medical_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 82.2% |
| medical_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 90.5% |
| medical_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 90.5% |
| medical_reasoning | relation | 100.0% | 0.0% | 100.0% | 89.7% |
| medical_reasoning | attribute | 100.0% | 0.0% | 100.0% | 93.9% |
| knowledge_reasoning | recognition | 100.0% | 0.0% | 100.0% | 90.8% |
| knowledge_reasoning | counting | 100.0% | 0.0% | 100.0% | 98.0% |
| knowledge_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.2% |
| knowledge_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 87.8% |
| knowledge_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.4% |
| knowledge_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 84.3% |
| knowledge_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 91.3% |
| knowledge_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.8% |
| knowledge_reasoning | relation | 100.0% | 0.0% | 100.0% | 94.5% |
| knowledge_reasoning | attribute | 100.0% | 0.0% | 100.0% | 94.4% |
| chart_reasoning | recognition | 100.0% | 0.0% | 100.0% | 90.6% |
| chart_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.8% |
| chart_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 92.2% |
| chart_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 86.9% |
| chart_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.3% |
| chart_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 83.9% |
| chart_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 88.4% |
| chart_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.5% |
| chart_reasoning | relation | 100.0% | 0.0% | 100.0% | 93.9% |
| chart_reasoning | attribute | 100.0% | 0.0% | 100.0% | 94.7% |
| document_reasoning | recognition | 100.0% | 0.0% | 100.0% | 90.0% |
| document_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.3% |
| document_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 92.7% |
| document_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 87.2% |
| document_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 91.1% |
| document_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 76.7% |
| document_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 88.1% |
| document_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.6% |
| document_reasoning | relation | 100.0% | 0.0% | 100.0% | 93.3% |
| document_reasoning | attribute | 100.0% | 0.0% | 100.0% | 94.6% |
| text_reading | recognition | 100.0% | 0.0% | 100.0% | 92.3% |
| text_reading | counting | 100.0% | 0.0% | 100.0% | 97.7% |
| text_reading | medical_reasoning | 100.0% | 0.0% | 100.0% | 92.3% |
| text_reading | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 84.6% |
| text_reading | chart_reasoning | 100.0% | 0.0% | 100.0% | 91.8% |
| text_reading | document_reasoning | 100.0% | 0.0% | 100.0% | 76.2% |
| text_reading | text_reading | 100.0% | 0.0% | 100.0% | 88.6% |
| text_reading | diagram_reasoning | 100.0% | 0.0% | 100.0% | 94.9% |
| text_reading | relation | 100.0% | 0.0% | 100.0% | 92.4% |
| text_reading | attribute | 100.0% | 0.0% | 100.0% | 94.9% |
| diagram_reasoning | recognition | 100.0% | 0.0% | 100.0% | 90.5% |
| diagram_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.8% |
| diagram_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 94.4% |
| diagram_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 86.2% |
| diagram_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 92.2% |
| diagram_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 78.6% |
| diagram_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 88.6% |
| diagram_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 94.0% |
| diagram_reasoning | relation | 100.0% | 0.0% | 100.0% | 94.2% |
| diagram_reasoning | attribute | 100.0% | 0.0% | 100.0% | 94.3% |
| relation | recognition | 100.0% | 0.0% | 100.0% | 90.9% |
| relation | counting | 100.0% | 0.0% | 100.0% | 94.5% |
| relation | medical_reasoning | 100.0% | 0.0% | 100.0% | 91.6% |
| relation | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 85.9% |
| relation | chart_reasoning | 100.0% | 0.0% | 100.0% | 86.4% |
| relation | document_reasoning | 100.0% | 0.0% | 100.0% | 80.4% |
| relation | text_reading | 100.0% | 0.0% | 100.0% | 87.3% |
| relation | diagram_reasoning | 100.0% | 0.0% | 100.0% | 94.5% |
| relation | relation | 100.0% | 0.0% | 100.0% | 94.1% |
| relation | attribute | 100.0% | 0.0% | 100.0% | 94.5% |
| attribute | recognition | 100.0% | 0.0% | 100.0% | 90.9% |
| attribute | counting | 100.0% | 0.0% | 100.0% | 95.3% |
| attribute | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.7% |
| attribute | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 86.0% |
| attribute | chart_reasoning | 100.0% | 0.0% | 100.0% | 94.0% |
| attribute | document_reasoning | 100.0% | 0.0% | 100.0% | 80.4% |
| attribute | text_reading | 100.0% | 0.0% | 100.0% | 89.3% |
| attribute | diagram_reasoning | 100.0% | 0.0% | 100.0% | 94.0% |
| attribute | relation | 100.0% | 0.0% | 100.0% | 93.6% |
| attribute | attribute | 100.0% | 0.0% | 100.0% | 95.7% |
