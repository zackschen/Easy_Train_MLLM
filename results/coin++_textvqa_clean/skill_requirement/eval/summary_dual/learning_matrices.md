# CoIN++ Skill Requirement Dual Evaluation

The standard and LLM-Judge tracks are independent. The standard track uses a registered source-benchmark metric when possible and normalized answer comparison otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below report that score normalized to [0, 1].

## Continual Summary

| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| Standard | 0.3381 | 0.3950 | 0.3812 | 0.0592 | -0.0479 |
| LLM Judge | 0.3666 | 0.4276 | 0.4023 | 0.0493 | -0.0397 |

## Standard Score Matrix

| Trained until | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recognition | 0.5441 | 0.1876 | 0.3060 | 0.3605 | 0.1177 | 0.1716 | 0.2933 | 0.1427 | 0.3788 | 0.4432 |
| counting | 0.5146 | 0.3295 | 0.2750 | 0.3197 | 0.1080 | 0.0961 | 0.2250 | 0.1248 | 0.3867 | 0.3859 |
| medical_reasoning | 0.5094 | 0.3294 | 0.3990 | 0.3441 | 0.1295 | 0.1355 | 0.2570 | 0.1694 | 0.3722 | 0.4341 |
| knowledge_reasoning | 0.5303 | 0.3318 | 0.3970 | 0.4355 | 0.1361 | 0.1280 | 0.2302 | 0.1794 | 0.3666 | 0.4137 |
| chart_reasoning | 0.5358 | 0.3452 | 0.4000 | 0.4158 | 0.2738 | 0.1744 | 0.2921 | 0.1956 | 0.3682 | 0.4233 |
| document_reasoning | 0.4968 | 0.3675 | 0.4070 | 0.4190 | 0.2967 | 0.2701 | 0.3081 | 0.1826 | 0.3623 | 0.4296 |
| text_reading | 0.5317 | 0.3396 | 0.4010 | 0.4223 | 0.2973 | 0.2857 | 0.3722 | 0.1888 | 0.3985 | 0.4113 |
| diagram_reasoning | 0.5305 | 0.3465 | 0.3870 | 0.4171 | 0.2749 | 0.2328 | 0.3768 | 0.2278 | 0.3868 | 0.3877 |
| relation | 0.4408 | 0.2737 | 0.3200 | 0.3484 | 0.2377 | 0.2376 | 0.3298 | 0.1945 | 0.4247 | 0.4329 |
| attribute | 0.4925 | 0.3083 | 0.3410 | 0.3654 | 0.2082 | 0.2030 | 0.2868 | 0.2036 | 0.4364 | 0.5354 |

## LLM-Judge Score Matrix

| Trained until | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recognition | 0.6051 | 0.1909 | 0.3510 | 0.4912 | 0.0997 | 0.1447 | 0.3186 | 0.1836 | 0.4251 | 0.4894 |
| counting | 0.5699 | 0.3370 | 0.3039 | 0.4142 | 0.1059 | 0.0905 | 0.2569 | 0.1836 | 0.4259 | 0.4177 |
| medical_reasoning | 0.5756 | 0.3314 | 0.4486 | 0.4736 | 0.1205 | 0.1086 | 0.2891 | 0.2176 | 0.4072 | 0.4766 |
| knowledge_reasoning | 0.5933 | 0.3321 | 0.4390 | 0.5345 | 0.1179 | 0.1131 | 0.2536 | 0.2312 | 0.4027 | 0.4597 |
| chart_reasoning | 0.6022 | 0.3489 | 0.4518 | 0.5116 | 0.2431 | 0.1242 | 0.3027 | 0.2315 | 0.4070 | 0.4668 |
| document_reasoning | 0.5653 | 0.3702 | 0.4565 | 0.5194 | 0.2624 | 0.1794 | 0.3257 | 0.2159 | 0.3933 | 0.4763 |
| text_reading | 0.5960 | 0.3376 | 0.4504 | 0.5170 | 0.2638 | 0.1984 | 0.3754 | 0.2099 | 0.4158 | 0.4588 |
| diagram_reasoning | 0.5840 | 0.3527 | 0.4197 | 0.5312 | 0.2509 | 0.1849 | 0.3730 | 0.2596 | 0.4309 | 0.4287 |
| relation | 0.5123 | 0.2951 | 0.3767 | 0.4501 | 0.2236 | 0.1652 | 0.3404 | 0.2308 | 0.4683 | 0.4675 |
| attribute | 0.5563 | 0.3191 | 0.3990 | 0.4656 | 0.1883 | 0.1512 | 0.2955 | 0.2452 | 0.4738 | 0.5720 |

## Standard-Score Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| recognition | 0.5441 | 0.5441 | 0.4925 | 0.0517 | -0.0517 |
| counting | 0.3295 | 0.3675 | 0.3083 | 0.0592 | -0.0212 |
| medical_reasoning | 0.3990 | 0.4070 | 0.3410 | 0.0660 | -0.0580 |
| knowledge_reasoning | 0.4355 | 0.4355 | 0.3654 | 0.0701 | -0.0701 |
| chart_reasoning | 0.2738 | 0.2973 | 0.2082 | 0.0891 | -0.0656 |
| document_reasoning | 0.2701 | 0.2857 | 0.2030 | 0.0827 | -0.0670 |
| text_reading | 0.3722 | 0.3768 | 0.2868 | 0.0901 | -0.0855 |
| diagram_reasoning | 0.2278 | 0.2278 | 0.2036 | 0.0241 | -0.0241 |
| relation | 0.4247 | 0.4364 | 0.4364 | 0.0000 | 0.0117 |
| attribute | 0.5354 | 0.5354 | 0.5354 | 0.0000 | 0.0000 |

## LLM-Judge Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| recognition | 0.6051 | 0.6051 | 0.5563 | 0.0488 | -0.0488 |
| counting | 0.3370 | 0.3702 | 0.3191 | 0.0511 | -0.0179 |
| medical_reasoning | 0.4486 | 0.4565 | 0.3990 | 0.0575 | -0.0496 |
| knowledge_reasoning | 0.5345 | 0.5345 | 0.4656 | 0.0689 | -0.0689 |
| chart_reasoning | 0.2431 | 0.2638 | 0.1883 | 0.0755 | -0.0548 |
| document_reasoning | 0.1794 | 0.1984 | 0.1512 | 0.0472 | -0.0282 |
| text_reading | 0.3754 | 0.3754 | 0.2955 | 0.0799 | -0.0799 |
| diagram_reasoning | 0.2596 | 0.2596 | 0.2452 | 0.0144 | -0.0144 |
| relation | 0.4683 | 0.4738 | 0.4738 | 0.0000 | 0.0055 |
| attribute | 0.5720 | 0.5720 | 0.5720 | 0.0000 | 0.0000 |

## Coverage And Agreement

| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |
|---|---|---:|---:|---:|---:|
| recognition | recognition | 100.0% | 0.0% | 100.0% | 91.8% |
| recognition | counting | 100.0% | 0.0% | 100.0% | 96.9% |
| recognition | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.5% |
| recognition | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 84.0% |
| recognition | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.5% |
| recognition | document_reasoning | 100.0% | 0.0% | 100.0% | 83.3% |
| recognition | text_reading | 100.0% | 0.0% | 100.0% | 90.4% |
| recognition | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.6% |
| recognition | relation | 100.0% | 0.0% | 100.0% | 93.0% |
| recognition | attribute | 100.0% | 0.0% | 100.0% | 94.7% |
| counting | recognition | 100.0% | 0.0% | 100.0% | 92.4% |
| counting | counting | 100.0% | 0.0% | 100.0% | 96.6% |
| counting | medical_reasoning | 100.0% | 0.0% | 100.0% | 95.4% |
| counting | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 87.3% |
| counting | chart_reasoning | 100.0% | 0.0% | 100.0% | 97.3% |
| counting | document_reasoning | 100.0% | 0.0% | 100.0% | 90.2% |
| counting | text_reading | 100.0% | 0.0% | 100.0% | 92.9% |
| counting | diagram_reasoning | 100.0% | 0.0% | 100.0% | 93.6% |
| counting | relation | 100.0% | 0.0% | 100.0% | 94.5% |
| counting | attribute | 100.0% | 0.0% | 100.0% | 96.1% |
| medical_reasoning | recognition | 100.0% | 0.0% | 100.0% | 90.3% |
| medical_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.4% |
| medical_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.5% |
| medical_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 81.9% |
| medical_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.0% |
| medical_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 83.9% |
| medical_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 90.6% |
| medical_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 89.1% |
| medical_reasoning | relation | 100.0% | 0.0% | 100.0% | 88.7% |
| medical_reasoning | attribute | 100.0% | 0.0% | 100.0% | 92.9% |
| knowledge_reasoning | recognition | 100.0% | 0.0% | 100.0% | 90.9% |
| knowledge_reasoning | counting | 100.0% | 0.0% | 100.0% | 98.2% |
| knowledge_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.3% |
| knowledge_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 87.8% |
| knowledge_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 95.0% |
| knowledge_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 85.5% |
| knowledge_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 93.2% |
| knowledge_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.8% |
| knowledge_reasoning | relation | 100.0% | 0.0% | 100.0% | 94.3% |
| knowledge_reasoning | attribute | 100.0% | 0.0% | 100.0% | 94.7% |
| chart_reasoning | recognition | 100.0% | 0.0% | 100.0% | 90.7% |
| chart_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.6% |
| chart_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 92.6% |
| chart_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 86.7% |
| chart_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.6% |
| chart_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 83.7% |
| chart_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 88.8% |
| chart_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.9% |
| chart_reasoning | relation | 100.0% | 0.0% | 100.0% | 93.1% |
| chart_reasoning | attribute | 100.0% | 0.0% | 100.0% | 94.5% |
| document_reasoning | recognition | 100.0% | 0.0% | 100.0% | 91.0% |
| document_reasoning | counting | 100.0% | 0.0% | 100.0% | 98.4% |
| document_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 93.1% |
| document_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 87.1% |
| document_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 91.5% |
| document_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 75.8% |
| document_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 89.0% |
| document_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 92.8% |
| document_reasoning | relation | 100.0% | 0.0% | 100.0% | 92.4% |
| document_reasoning | attribute | 100.0% | 0.0% | 100.0% | 94.3% |
| text_reading | recognition | 100.0% | 0.0% | 100.0% | 91.0% |
| text_reading | counting | 100.0% | 0.0% | 100.0% | 98.1% |
| text_reading | medical_reasoning | 100.0% | 0.0% | 100.0% | 92.3% |
| text_reading | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 88.3% |
| text_reading | chart_reasoning | 100.0% | 0.0% | 100.0% | 90.7% |
| text_reading | document_reasoning | 100.0% | 0.0% | 100.0% | 76.6% |
| text_reading | text_reading | 100.0% | 0.0% | 100.0% | 88.1% |
| text_reading | diagram_reasoning | 100.0% | 0.0% | 100.0% | 93.2% |
| text_reading | relation | 100.0% | 0.0% | 100.0% | 91.5% |
| text_reading | attribute | 100.0% | 0.0% | 100.0% | 94.3% |
| diagram_reasoning | recognition | 100.0% | 0.0% | 100.0% | 91.2% |
| diagram_reasoning | counting | 100.0% | 0.0% | 100.0% | 97.6% |
| diagram_reasoning | medical_reasoning | 100.0% | 0.0% | 100.0% | 92.8% |
| diagram_reasoning | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 85.8% |
| diagram_reasoning | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.6% |
| diagram_reasoning | document_reasoning | 100.0% | 0.0% | 100.0% | 79.7% |
| diagram_reasoning | text_reading | 100.0% | 0.0% | 100.0% | 88.7% |
| diagram_reasoning | diagram_reasoning | 100.0% | 0.0% | 100.0% | 94.7% |
| diagram_reasoning | relation | 100.0% | 0.0% | 100.0% | 93.8% |
| diagram_reasoning | attribute | 100.0% | 0.0% | 100.0% | 94.9% |
| relation | recognition | 100.0% | 0.0% | 100.0% | 90.4% |
| relation | counting | 100.0% | 0.0% | 100.0% | 96.0% |
| relation | medical_reasoning | 100.0% | 0.0% | 100.0% | 91.9% |
| relation | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 86.1% |
| relation | chart_reasoning | 100.0% | 0.0% | 100.0% | 91.0% |
| relation | document_reasoning | 100.0% | 0.0% | 100.0% | 77.2% |
| relation | text_reading | 100.0% | 0.0% | 100.0% | 87.0% |
| relation | diagram_reasoning | 100.0% | 0.0% | 100.0% | 94.4% |
| relation | relation | 100.0% | 0.0% | 100.0% | 93.4% |
| relation | attribute | 100.0% | 0.0% | 100.0% | 95.4% |
| attribute | recognition | 100.0% | 0.0% | 100.0% | 91.2% |
| attribute | counting | 100.0% | 0.0% | 100.0% | 97.0% |
| attribute | medical_reasoning | 100.0% | 0.0% | 100.0% | 92.5% |
| attribute | knowledge_reasoning | 100.0% | 0.0% | 100.0% | 86.1% |
| attribute | chart_reasoning | 100.0% | 0.0% | 100.0% | 93.7% |
| attribute | document_reasoning | 100.0% | 0.0% | 100.0% | 80.0% |
| attribute | text_reading | 100.0% | 0.0% | 100.0% | 88.2% |
| attribute | diagram_reasoning | 100.0% | 0.0% | 100.0% | 93.9% |
| attribute | relation | 100.0% | 0.0% | 100.0% | 93.9% |
| attribute | attribute | 100.0% | 0.0% | 100.0% | 95.9% |
