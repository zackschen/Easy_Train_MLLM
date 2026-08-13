# Skill Requirement Module Dual Evaluation

Standard and LLM-Judge results are reported independently; no fallback or hybrid score is used.

## Standard Continual Metrics

| Mode | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| vision_only | 0.2448 | 0.1602 | 0.1770 | 0.0041 | 0.0753 |
| projector_only | 0.2877 | 0.2860 | 0.2867 | 0.0141 | 0.0011 |
| llm_only | 0.3183 | 0.3924 | 0.3853 | 0.0757 | -0.0745 |

### Standard Final Scores By Task

| Mode | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| vision_only | 0.3583 | 0.2064 | 0.1880 | 0.2542 | 0.1423 | 0.1477 | 0.2635 | 0.0959 | 0.3331 | 0.4587 |
| projector_only | 0.4466 | 0.2698 | 0.1920 | 0.3149 | 0.1531 | 0.1929 | 0.3188 | 0.1200 | 0.3796 | 0.4898 |
| llm_only | 0.4465 | 0.2110 | 0.3360 | 0.3581 | 0.1963 | 0.1963 | 0.2980 | 0.2115 | 0.4007 | 0.5289 |

## LLM Judge Continual Metrics

| Mode | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| vision_only | 0.2813 | 0.2756 | 0.2699 | 0.0081 | 0.0127 |
| projector_only | 0.3234 | 0.3250 | 0.3213 | 0.0086 | 0.0023 |
| llm_only | 0.3455 | 0.4273 | 0.4082 | 0.0714 | -0.0697 |

### LLM Judge Final Scores By Task

| Mode | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| vision_only | 0.4098 | 0.2139 | 0.2405 | 0.3624 | 0.1266 | 0.1200 | 0.2958 | 0.1190 | 0.3974 | 0.5275 |
| projector_only | 0.4917 | 0.2778 | 0.2498 | 0.4299 | 0.1370 | 0.1497 | 0.3466 | 0.1506 | 0.4409 | 0.5604 |
| llm_only | 0.5105 | 0.2281 | 0.3709 | 0.4546 | 0.1829 | 0.1458 | 0.3080 | 0.2441 | 0.4456 | 0.5645 |

## Per-Task Forgetting

| Track | Mode | Task | At learning | Best | Final | Forgetting | BWT |
|---|---|---|---:|---:|---:|---:|---:|
| standard | vision_only | recognition | 0.0883 | 0.3617 | 0.3583 | 0.0034 | 0.2700 |
| standard | vision_only | counting | 0.0612 | 0.2065 | 0.2064 | 0.0001 | 0.1452 |
| standard | vision_only | medical_reasoning | 0.1670 | 0.2040 | 0.1880 | 0.0160 | 0.0210 |
| standard | vision_only | knowledge_reasoning | 0.1285 | 0.2542 | 0.2542 | 0.0000 | 0.1257 |
| standard | vision_only | chart_reasoning | 0.1470 | 0.1592 | 0.1423 | 0.0170 | -0.0048 |
| standard | vision_only | document_reasoning | 0.1063 | 0.1477 | 0.1477 | 0.0000 | 0.0414 |
| standard | vision_only | text_reading | 0.2007 | 0.2635 | 0.2635 | 0.0000 | 0.0628 |
| standard | vision_only | diagram_reasoning | 0.0927 | 0.0959 | 0.0959 | 0.0000 | 0.0032 |
| standard | vision_only | relation | 0.3199 | 0.3331 | 0.3331 | 0.0000 | 0.0131 |
| standard | vision_only | attribute | 0.4587 | 0.4587 | 0.4587 | 0.0000 | 0.0000 |
| standard | projector_only | recognition | 0.3554 | 0.4466 | 0.4466 | 0.0000 | 0.0912 |
| standard | projector_only | counting | 0.2534 | 0.2699 | 0.2698 | 0.0001 | 0.0164 |
| standard | projector_only | medical_reasoning | 0.2410 | 0.2410 | 0.1920 | 0.0490 | -0.0490 |
| standard | projector_only | knowledge_reasoning | 0.3107 | 0.3254 | 0.3149 | 0.0105 | 0.0042 |
| standard | projector_only | chart_reasoning | 0.1835 | 0.1865 | 0.1531 | 0.0334 | -0.0304 |
| standard | projector_only | document_reasoning | 0.2071 | 0.2171 | 0.1929 | 0.0242 | -0.0142 |
| standard | projector_only | text_reading | 0.3211 | 0.3219 | 0.3188 | 0.0031 | -0.0023 |
| standard | projector_only | diagram_reasoning | 0.1233 | 0.1241 | 0.1200 | 0.0041 | -0.0033 |
| standard | projector_only | relation | 0.3821 | 0.3821 | 0.3796 | 0.0025 | -0.0025 |
| standard | projector_only | attribute | 0.4898 | 0.4898 | 0.4898 | 0.0000 | 0.0000 |
| standard | llm_only | recognition | 0.5562 | 0.5562 | 0.4465 | 0.1097 | -0.1097 |
| standard | llm_only | counting | 0.3527 | 0.3527 | 0.2110 | 0.1417 | -0.1417 |
| standard | llm_only | medical_reasoning | 0.3910 | 0.3930 | 0.3360 | 0.0570 | -0.0550 |
| standard | llm_only | knowledge_reasoning | 0.4367 | 0.4367 | 0.3581 | 0.0786 | -0.0786 |
| standard | llm_only | chart_reasoning | 0.2738 | 0.2828 | 0.1963 | 0.0865 | -0.0775 |
| standard | llm_only | document_reasoning | 0.2753 | 0.2753 | 0.1963 | 0.0791 | -0.0791 |
| standard | llm_only | text_reading | 0.3863 | 0.3863 | 0.2980 | 0.0882 | -0.0882 |
| standard | llm_only | diagram_reasoning | 0.2160 | 0.2160 | 0.2115 | 0.0045 | -0.0045 |
| standard | llm_only | relation | 0.4365 | 0.4365 | 0.4007 | 0.0359 | -0.0359 |
| standard | llm_only | attribute | 0.5289 | 0.5289 | 0.5289 | 0.0000 | 0.0000 |
| llm_judge | vision_only | recognition | 0.3589 | 0.4182 | 0.4098 | 0.0084 | 0.0509 |
| llm_judge | vision_only | counting | 0.1615 | 0.2211 | 0.2139 | 0.0072 | 0.0524 |
| llm_judge | vision_only | medical_reasoning | 0.2665 | 0.2710 | 0.2405 | 0.0305 | -0.0260 |
| llm_judge | vision_only | knowledge_reasoning | 0.3422 | 0.3689 | 0.3624 | 0.0065 | 0.0202 |
| llm_judge | vision_only | chart_reasoning | 0.1367 | 0.1401 | 0.1266 | 0.0135 | -0.0101 |
| llm_judge | vision_only | document_reasoning | 0.1147 | 0.1264 | 0.1200 | 0.0064 | 0.0053 |
| llm_judge | vision_only | text_reading | 0.2919 | 0.2958 | 0.2958 | 0.0000 | 0.0039 |
| llm_judge | vision_only | diagram_reasoning | 0.1194 | 0.1194 | 0.1190 | 0.0004 | -0.0004 |
| llm_judge | vision_only | relation | 0.3795 | 0.3974 | 0.3974 | 0.0000 | 0.0179 |
| llm_judge | vision_only | attribute | 0.5275 | 0.5275 | 0.5275 | 0.0000 | 0.0000 |
| llm_judge | projector_only | recognition | 0.4287 | 0.4917 | 0.4917 | 0.0000 | 0.0630 |
| llm_judge | projector_only | counting | 0.2658 | 0.2778 | 0.2778 | 0.0000 | 0.0120 |
| llm_judge | projector_only | medical_reasoning | 0.2875 | 0.2875 | 0.2498 | 0.0377 | -0.0377 |
| llm_judge | projector_only | knowledge_reasoning | 0.4369 | 0.4369 | 0.4299 | 0.0070 | -0.0070 |
| llm_judge | projector_only | chart_reasoning | 0.1505 | 0.1612 | 0.1370 | 0.0242 | -0.0135 |
| llm_judge | projector_only | document_reasoning | 0.1489 | 0.1562 | 0.1497 | 0.0065 | 0.0008 |
| llm_judge | projector_only | text_reading | 0.3446 | 0.3487 | 0.3466 | 0.0021 | 0.0020 |
| llm_judge | projector_only | diagram_reasoning | 0.1502 | 0.1506 | 0.1506 | 0.0000 | 0.0004 |
| llm_judge | projector_only | relation | 0.4399 | 0.4409 | 0.4409 | 0.0000 | 0.0010 |
| llm_judge | projector_only | attribute | 0.5604 | 0.5604 | 0.5604 | 0.0000 | 0.0000 |
| llm_judge | llm_only | recognition | 0.6175 | 0.6175 | 0.5105 | 0.1070 | -0.1070 |
| llm_judge | llm_only | counting | 0.3604 | 0.3609 | 0.2281 | 0.1328 | -0.1323 |
| llm_judge | llm_only | medical_reasoning | 0.4507 | 0.4507 | 0.3709 | 0.0798 | -0.0798 |
| llm_judge | llm_only | knowledge_reasoning | 0.5307 | 0.5374 | 0.4546 | 0.0828 | -0.0761 |
| llm_judge | llm_only | chart_reasoning | 0.2408 | 0.2471 | 0.1829 | 0.0642 | -0.0579 |
| llm_judge | llm_only | document_reasoning | 0.1882 | 0.1900 | 0.1458 | 0.0442 | -0.0424 |
| llm_judge | llm_only | text_reading | 0.3977 | 0.3977 | 0.3080 | 0.0897 | -0.0897 |
| llm_judge | llm_only | diagram_reasoning | 0.2528 | 0.2528 | 0.2441 | 0.0087 | -0.0087 |
| llm_judge | llm_only | relation | 0.4789 | 0.4789 | 0.4456 | 0.0333 | -0.0333 |
| llm_judge | llm_only | attribute | 0.5645 | 0.5645 | 0.5645 | 0.0000 | 0.0000 |
