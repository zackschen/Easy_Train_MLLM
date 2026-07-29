# Visual Substrate Trainable-Module Comparison (relaxed_match)

## Overall Continual Metrics

| Mode | Final average | Mean seen accuracy | Mean at learning | Avg forgetting (old) | BWT (old) | Final-task score |
|---|---:|---:|---:|---:|---:|---:|
| vision_only | 0.1838 | 0.2211 | 0.1823 | 0.0116 | 0.0018 | 0.1610 |
| projector_only | 0.1957 | 0.2459 | 0.2005 | 0.0170 | -0.0058 | 0.1660 |
| llm_only | 0.2943 | 0.3711 | 0.3120 | 0.0272 | -0.0212 | 0.2440 |

## Final Scores by Task

| Mode | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| vision_only | 0.2540 | 0.2890 | 0.1360 | 0.1410 | 0.1220 | 0.1610 |
| projector_only | 0.2790 | 0.2760 | 0.1650 | 0.1510 | 0.1370 | 0.1660 |
| llm_only | 0.4160 | 0.4190 | 0.2200 | 0.1950 | 0.2720 | 0.2440 |

## Forgetting by Task

| Mode | Task | At learning | Best after learning | Final | Forgetting | Final - learning |
|---|---|---:|---:|---:|---:|---:|
| vision_only | natural_photo | 0.2380 | 0.2820 | 0.2540 | 0.0280 | 0.0160 |
| vision_only | medical | 0.3000 | 0.3030 | 0.2890 | 0.0140 | -0.0110 |
| vision_only | document | 0.1170 | 0.1360 | 0.1360 | 0.0000 | 0.0190 |
| vision_only | infographic | 0.1400 | 0.1410 | 0.1410 | 0.0000 | 0.0010 |
| vision_only | diagram | 0.1380 | 0.1380 | 0.1220 | 0.0160 | -0.0160 |
| vision_only | chart | 0.1610 | 0.1610 | 0.1610 | 0.0000 | 0.0000 |
| projector_only | natural_photo | 0.2890 | 0.3150 | 0.2790 | 0.0360 | -0.0100 |
| projector_only | medical | 0.2960 | 0.3040 | 0.2760 | 0.0280 | -0.0200 |
| projector_only | document | 0.1560 | 0.1670 | 0.1650 | 0.0020 | 0.0090 |
| projector_only | infographic | 0.1480 | 0.1590 | 0.1510 | 0.0080 | 0.0030 |
| projector_only | diagram | 0.1480 | 0.1480 | 0.1370 | 0.0110 | -0.0110 |
| projector_only | chart | 0.1660 | 0.1660 | 0.1660 | 0.0000 | 0.0000 |
| llm_only | natural_photo | 0.4810 | 0.4810 | 0.4160 | 0.0650 | -0.0650 |
| llm_only | medical | 0.4720 | 0.4720 | 0.4190 | 0.0530 | -0.0530 |
| llm_only | document | 0.2180 | 0.2370 | 0.2200 | 0.0170 | 0.0020 |
| llm_only | infographic | 0.1840 | 0.1950 | 0.1950 | 0.0000 | 0.0110 |
| llm_only | diagram | 0.2730 | 0.2730 | 0.2720 | 0.0010 | -0.0010 |
| llm_only | chart | 0.2440 | 0.2440 | 0.2440 | 0.0000 | 0.0000 |
