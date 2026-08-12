# Visual Substrate Trainable-Module Comparison (relaxed_match)

## Overall Continual Metrics

| Mode | Final average | Mean seen accuracy | Mean at learning | Avg forgetting (old) | BWT (old) | Final-task score |
|---|---:|---:|---:|---:|---:|---:|
| vision_only | 0.1922 | 0.2304 | 0.1893 | 0.0118 | 0.0034 | 0.1730 |
| projector_only | 0.2032 | 0.2533 | 0.2073 | 0.0156 | -0.0050 | 0.1710 |
| llm_only | 0.2973 | 0.3682 | 0.3192 | 0.0274 | -0.0262 | 0.2960 |

## Final Scores by Task

| Mode | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| vision_only | 0.2660 | 0.2910 | 0.1520 | 0.1390 | 0.1320 | 0.1730 |
| projector_only | 0.2780 | 0.2910 | 0.1720 | 0.1610 | 0.1460 | 0.1710 |
| llm_only | 0.4110 | 0.4420 | 0.1990 | 0.1770 | 0.2590 | 0.2960 |

## Forgetting by Task

| Mode | Task | At learning | Best after learning | Final | Forgetting | Final - learning |
|---|---|---:|---:|---:|---:|---:|
| vision_only | natural_photo | 0.2510 | 0.2980 | 0.2660 | 0.0320 | 0.0150 |
| vision_only | medical | 0.2990 | 0.2990 | 0.2910 | 0.0080 | -0.0080 |
| vision_only | document | 0.1230 | 0.1520 | 0.1520 | 0.0000 | 0.0290 |
| vision_only | infographic | 0.1560 | 0.1560 | 0.1390 | 0.0170 | -0.0170 |
| vision_only | diagram | 0.1340 | 0.1340 | 0.1320 | 0.0020 | -0.0020 |
| vision_only | chart | 0.1730 | 0.1730 | 0.1730 | 0.0000 | 0.0000 |
| projector_only | natural_photo | 0.2930 | 0.3230 | 0.2780 | 0.0450 | -0.0150 |
| projector_only | medical | 0.3090 | 0.3090 | 0.2910 | 0.0180 | -0.0180 |
| projector_only | document | 0.1620 | 0.1790 | 0.1720 | 0.0070 | 0.0100 |
| projector_only | infographic | 0.1590 | 0.1650 | 0.1610 | 0.0040 | 0.0020 |
| projector_only | diagram | 0.1500 | 0.1500 | 0.1460 | 0.0040 | -0.0040 |
| projector_only | chart | 0.1710 | 0.1710 | 0.1710 | 0.0000 | 0.0000 |
| llm_only | natural_photo | 0.4740 | 0.4740 | 0.4110 | 0.0630 | -0.0630 |
| llm_only | medical | 0.4630 | 0.4630 | 0.4420 | 0.0210 | -0.0210 |
| llm_only | document | 0.2210 | 0.2240 | 0.1990 | 0.0250 | -0.0220 |
| llm_only | infographic | 0.2050 | 0.2050 | 0.1770 | 0.0280 | -0.0280 |
| llm_only | diagram | 0.2560 | 0.2590 | 0.2590 | 0.0000 | 0.0030 |
| llm_only | chart | 0.2960 | 0.2960 | 0.2960 | 0.0000 | 0.0000 |
