# Visual Substrate Module Comparison

Scoring protocol: dataset-native metrics with LLM-Judge fallback; matrix metric: `primary_score`.

## Overall Continual Metrics

| Mode | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) | Final task |
|---|---:|---:|---:|---:|---:|---:|
| vision_only | 0.1065 | 0.0720 | 0.0639 | 0.0019 | 0.0511 | 0.1318 |
| projector_only | 0.1839 | 0.2148 | 0.1804 | 0.0147 | 0.0041 | 0.1519 |
| llm_only | 0.2844 | 0.3609 | 0.3246 | 0.0482 | -0.0482 | 0.2855 |

## Final Scores by Task

| Mode | natural_photo | medical | document | infographic | diagram | chart |
|---|---:|---:|---:|---:|---:|---:|
| vision_only | 0.0824 | 0.1660 | 0.0757 | 0.1010 | 0.0820 | 0.1318 |
| projector_only | 0.2912 | 0.2240 | 0.1840 | 0.1371 | 0.1153 | 0.1519 |
| llm_only | 0.3902 | 0.3980 | 0.2313 | 0.1763 | 0.2250 | 0.2855 |

## Forgetting by Task

| Mode | Task | At learning | Best | Final | Forgetting | BWT |
|---|---|---:|---:|---:|---:|---:|
| vision_only | natural_photo | 0.0396 | 0.0868 | 0.0824 | 0.0044 | 0.0428 |
| vision_only | medical | 0.0540 | 0.1700 | 0.1660 | 0.0040 | 0.1120 |
| vision_only | document | 0.0164 | 0.0757 | 0.0757 | 0.0000 | 0.0594 |
| vision_only | infographic | 0.0817 | 0.1020 | 0.1010 | 0.0010 | 0.0193 |
| vision_only | diagram | 0.0600 | 0.0820 | 0.0820 | 0.0000 | 0.0220 |
| vision_only | chart | 0.1318 | 0.1318 | 0.1318 | 0.0000 | 0.0000 |
| projector_only | natural_photo | 0.2247 | 0.2912 | 0.2912 | 0.0000 | 0.0665 |
| projector_only | medical | 0.2330 | 0.2400 | 0.2240 | 0.0160 | -0.0090 |
| projector_only | document | 0.1763 | 0.1908 | 0.1840 | 0.0068 | 0.0077 |
| projector_only | infographic | 0.1879 | 0.1879 | 0.1371 | 0.0507 | -0.0507 |
| projector_only | diagram | 0.1090 | 0.1153 | 0.1153 | 0.0000 | 0.0063 |
| projector_only | chart | 0.1519 | 0.1519 | 0.1519 | 0.0000 | 0.0000 |
| llm_only | natural_photo | 0.4435 | 0.4435 | 0.3902 | 0.0533 | -0.0533 |
| llm_only | medical | 0.4510 | 0.4510 | 0.3980 | 0.0530 | -0.0530 |
| llm_only | document | 0.2884 | 0.2884 | 0.2313 | 0.0570 | -0.0570 |
| llm_only | infographic | 0.2409 | 0.2409 | 0.1763 | 0.0647 | -0.0647 |
| llm_only | diagram | 0.2380 | 0.2380 | 0.2250 | 0.0130 | -0.0130 |
| llm_only | chart | 0.2855 | 0.2855 | 0.2855 | 0.0000 | 0.0000 |
