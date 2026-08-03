# Visual Substrate Module Dual Evaluation

Standard and LLM-Judge results are reported independently; no fallback or hybrid score is used.

## Standard Continual Metrics

| Mode | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| vision_only | 0.1065 | 0.0720 | 0.0639 | 0.0019 | 0.0511 |
| projector_only | 0.1839 | 0.2148 | 0.1804 | 0.0147 | 0.0041 |
| llm_only | 0.2844 | 0.3609 | 0.3246 | 0.0482 | -0.0482 |

### Standard Final Scores By Task

| Mode | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| vision_only | 0.0824 | 0.1660 | 0.0757 | 0.1010 | 0.0820 | 0.1318 |
| projector_only | 0.2912 | 0.2240 | 0.1840 | 0.1371 | 0.1153 | 0.1519 |
| llm_only | 0.3902 | 0.3980 | 0.2313 | 0.1763 | 0.2250 | 0.2855 |

## LLM Judge Continual Metrics

| Mode | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| vision_only | 0.1928 | 0.2362 | 0.1747 | 0.0040 | 0.0217 |
| projector_only | 0.2199 | 0.2760 | 0.2087 | 0.0021 | 0.0134 |
| llm_only | 0.2963 | 0.3877 | 0.3215 | 0.0304 | -0.0302 |

### LLM Judge Final Scores By Task

| Mode | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| vision_only | 0.3378 | 0.2810 | 0.1347 | 0.1442 | 0.1090 | 0.1504 |
| projector_only | 0.4041 | 0.2836 | 0.1744 | 0.1581 | 0.1304 | 0.1689 |
| llm_only | 0.4468 | 0.4286 | 0.2100 | 0.1878 | 0.2550 | 0.2496 |

## Per-Task Forgetting

| Track | Mode | Task | At learning | Best | Final | Forgetting | BWT |
|---|---|---|---:|---:|---:|---:|---:|
| standard | vision_only | natural_photo | 0.0396 | 0.0868 | 0.0824 | 0.0044 | 0.0428 |
| standard | vision_only | medical | 0.0540 | 0.1700 | 0.1660 | 0.0040 | 0.1120 |
| standard | vision_only | document | 0.0164 | 0.0757 | 0.0757 | 0.0000 | 0.0594 |
| standard | vision_only | infographic | 0.0817 | 0.1020 | 0.1010 | 0.0010 | 0.0193 |
| standard | vision_only | diagram | 0.0600 | 0.0820 | 0.0820 | 0.0000 | 0.0220 |
| standard | vision_only | chart | 0.1318 | 0.1318 | 0.1318 | 0.0000 | 0.0000 |
| standard | projector_only | natural_photo | 0.2247 | 0.2912 | 0.2912 | 0.0000 | 0.0665 |
| standard | projector_only | medical | 0.2330 | 0.2400 | 0.2240 | 0.0160 | -0.0090 |
| standard | projector_only | document | 0.1763 | 0.1908 | 0.1840 | 0.0068 | 0.0077 |
| standard | projector_only | infographic | 0.1879 | 0.1879 | 0.1371 | 0.0507 | -0.0507 |
| standard | projector_only | diagram | 0.1090 | 0.1153 | 0.1153 | 0.0000 | 0.0063 |
| standard | projector_only | chart | 0.1519 | 0.1519 | 0.1519 | 0.0000 | 0.0000 |
| standard | llm_only | natural_photo | 0.4435 | 0.4435 | 0.3902 | 0.0533 | -0.0533 |
| standard | llm_only | medical | 0.4510 | 0.4510 | 0.3980 | 0.0530 | -0.0530 |
| standard | llm_only | document | 0.2884 | 0.2884 | 0.2313 | 0.0570 | -0.0570 |
| standard | llm_only | infographic | 0.2409 | 0.2409 | 0.1763 | 0.0647 | -0.0647 |
| standard | llm_only | diagram | 0.2380 | 0.2380 | 0.2250 | 0.0130 | -0.0130 |
| standard | llm_only | chart | 0.2855 | 0.2855 | 0.2855 | 0.0000 | 0.0000 |
| llm_judge | vision_only | natural_photo | 0.2781 | 0.3530 | 0.3378 | 0.0152 | 0.0597 |
| llm_judge | vision_only | medical | 0.2615 | 0.2830 | 0.2810 | 0.0020 | 0.0195 |
| llm_judge | vision_only | document | 0.1218 | 0.1375 | 0.1347 | 0.0028 | 0.0129 |
| llm_judge | vision_only | infographic | 0.1276 | 0.1442 | 0.1442 | 0.0000 | 0.0166 |
| llm_judge | vision_only | diagram | 0.1090 | 0.1090 | 0.1090 | 0.0000 | 0.0000 |
| llm_judge | vision_only | chart | 0.1504 | 0.1504 | 0.1504 | 0.0000 | 0.0000 |
| llm_judge | projector_only | natural_photo | 0.3570 | 0.4041 | 0.4041 | 0.0000 | 0.0471 |
| llm_judge | projector_only | medical | 0.2942 | 0.2942 | 0.2836 | 0.0106 | -0.0106 |
| llm_judge | projector_only | document | 0.1580 | 0.1744 | 0.1744 | 0.0000 | 0.0164 |
| llm_judge | projector_only | infographic | 0.1506 | 0.1581 | 0.1581 | 0.0000 | 0.0075 |
| llm_judge | projector_only | diagram | 0.1237 | 0.1304 | 0.1304 | 0.0000 | 0.0067 |
| llm_judge | projector_only | chart | 0.1689 | 0.1689 | 0.1689 | 0.0000 | 0.0000 |
| llm_judge | llm_only | natural_photo | 0.5118 | 0.5118 | 0.4468 | 0.0650 | -0.0650 |
| llm_judge | llm_only | medical | 0.4872 | 0.4872 | 0.4286 | 0.0586 | -0.0586 |
| llm_judge | llm_only | document | 0.2205 | 0.2209 | 0.2100 | 0.0109 | -0.0105 |
| llm_judge | llm_only | infographic | 0.1940 | 0.1944 | 0.1878 | 0.0066 | -0.0062 |
| llm_judge | llm_only | diagram | 0.2658 | 0.2658 | 0.2550 | 0.0108 | -0.0108 |
| llm_judge | llm_only | chart | 0.2496 | 0.2496 | 0.2496 | 0.0000 | 0.0000 |
