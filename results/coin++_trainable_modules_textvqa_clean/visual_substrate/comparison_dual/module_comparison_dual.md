# Visual Substrate Module Dual Evaluation

Standard and LLM-Judge results are reported independently; no fallback or hybrid score is used.

## Standard Continual Metrics

| Mode | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| vision_only | 0.1298 | 0.0994 | 0.0882 | 0.0066 | 0.0500 |
| projector_only | 0.1952 | 0.2320 | 0.1980 | 0.0146 | -0.0033 |
| llm_only | 0.2902 | 0.3554 | 0.3197 | 0.0390 | -0.0354 |

### Standard Final Scores By Task

| Mode | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| vision_only | 0.1084 | 0.2160 | 0.0955 | 0.1280 | 0.0910 | 0.1400 |
| projector_only | 0.2978 | 0.2390 | 0.2024 | 0.1450 | 0.1140 | 0.1729 |
| llm_only | 0.3809 | 0.4100 | 0.2342 | 0.1783 | 0.2160 | 0.3218 |

## LLM Judge Continual Metrics

| Mode | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| vision_only | 0.2019 | 0.2555 | 0.1922 | 0.0026 | 0.0116 |
| projector_only | 0.2291 | 0.2827 | 0.2171 | 0.0013 | 0.0144 |
| llm_only | 0.3040 | 0.3832 | 0.3215 | 0.0246 | -0.0209 |

### LLM Judge Final Scores By Task

| Mode | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| vision_only | 0.3550 | 0.2900 | 0.1441 | 0.1423 | 0.1144 | 0.1654 |
| projector_only | 0.4125 | 0.2961 | 0.1855 | 0.1680 | 0.1366 | 0.1758 |
| llm_only | 0.4484 | 0.4565 | 0.1908 | 0.1777 | 0.2563 | 0.2946 |

## Per-Task Forgetting

| Track | Mode | Task | At learning | Best | Final | Forgetting | BWT |
|---|---|---|---:|---:|---:|---:|---:|
| standard | vision_only | natural_photo | 0.0596 | 0.1325 | 0.1084 | 0.0241 | 0.0488 |
| standard | vision_only | medical | 0.1130 | 0.2160 | 0.2160 | 0.0000 | 0.1030 |
| standard | vision_only | document | 0.0191 | 0.0955 | 0.0955 | 0.0000 | 0.0765 |
| standard | vision_only | infographic | 0.1183 | 0.1368 | 0.1280 | 0.0088 | 0.0097 |
| standard | vision_only | diagram | 0.0790 | 0.0910 | 0.0910 | 0.0000 | 0.0120 |
| standard | vision_only | chart | 0.1400 | 0.1400 | 0.1400 | 0.0000 | 0.0000 |
| standard | projector_only | natural_photo | 0.2605 | 0.3071 | 0.2978 | 0.0093 | 0.0373 |
| standard | projector_only | medical | 0.2470 | 0.2470 | 0.2390 | 0.0080 | -0.0080 |
| standard | projector_only | document | 0.1926 | 0.2024 | 0.2024 | 0.0000 | 0.0099 |
| standard | projector_only | infographic | 0.1979 | 0.1979 | 0.1450 | 0.0529 | -0.0529 |
| standard | projector_only | diagram | 0.1170 | 0.1170 | 0.1140 | 0.0030 | -0.0030 |
| standard | projector_only | chart | 0.1729 | 0.1729 | 0.1729 | 0.0000 | 0.0000 |
| standard | llm_only | natural_photo | 0.4329 | 0.4329 | 0.3809 | 0.0520 | -0.0520 |
| standard | llm_only | medical | 0.4370 | 0.4370 | 0.4100 | 0.0270 | -0.0270 |
| standard | llm_only | document | 0.2807 | 0.2807 | 0.2342 | 0.0465 | -0.0465 |
| standard | llm_only | infographic | 0.2477 | 0.2477 | 0.1783 | 0.0694 | -0.0694 |
| standard | llm_only | diagram | 0.1980 | 0.2160 | 0.2160 | 0.0000 | 0.0180 |
| standard | llm_only | chart | 0.3218 | 0.3218 | 0.3218 | 0.0000 | 0.0000 |
| llm_judge | vision_only | natural_photo | 0.3319 | 0.3663 | 0.3550 | 0.0113 | 0.0231 |
| llm_judge | vision_only | medical | 0.2826 | 0.2900 | 0.2900 | 0.0000 | 0.0074 |
| llm_judge | vision_only | document | 0.1287 | 0.1441 | 0.1441 | 0.0000 | 0.0154 |
| llm_judge | vision_only | infographic | 0.1284 | 0.1423 | 0.1423 | 0.0000 | 0.0139 |
| llm_judge | vision_only | diagram | 0.1161 | 0.1161 | 0.1144 | 0.0017 | -0.0017 |
| llm_judge | vision_only | chart | 0.1654 | 0.1654 | 0.1654 | 0.0000 | 0.0000 |
| llm_judge | projector_only | natural_photo | 0.3632 | 0.4125 | 0.4125 | 0.0000 | 0.0493 |
| llm_judge | projector_only | medical | 0.3026 | 0.3026 | 0.2961 | 0.0065 | -0.0065 |
| llm_judge | projector_only | document | 0.1648 | 0.1855 | 0.1855 | 0.0000 | 0.0207 |
| llm_judge | projector_only | infographic | 0.1604 | 0.1680 | 0.1680 | 0.0000 | 0.0076 |
| llm_judge | projector_only | diagram | 0.1359 | 0.1366 | 0.1366 | 0.0000 | 0.0007 |
| llm_judge | projector_only | chart | 0.1758 | 0.1758 | 0.1758 | 0.0000 | 0.0000 |
| llm_judge | llm_only | natural_photo | 0.4965 | 0.4965 | 0.4484 | 0.0481 | -0.0481 |
| llm_judge | llm_only | medical | 0.4764 | 0.4764 | 0.4565 | 0.0200 | -0.0200 |
| llm_judge | llm_only | document | 0.2150 | 0.2160 | 0.1908 | 0.0252 | -0.0242 |
| llm_judge | llm_only | infographic | 0.2075 | 0.2075 | 0.1777 | 0.0298 | -0.0298 |
| llm_judge | llm_only | diagram | 0.2387 | 0.2563 | 0.2563 | 0.0000 | 0.0176 |
| llm_judge | llm_only | chart | 0.2946 | 0.2946 | 0.2946 | 0.0000 | 0.0000 |
