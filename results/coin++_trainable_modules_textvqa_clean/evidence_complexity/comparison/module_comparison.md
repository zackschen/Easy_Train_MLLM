# Evidence Complexity Trainable-Module Comparison (relaxed_match)

## Overall Continual Metrics

| Mode | Final average | Mean seen accuracy | Mean at learning | Avg forgetting (old) | BWT (old) | Final-task score |
|---|---:|---:|---:|---:|---:|---:|
| vision_only | 0.2228 | 0.2066 | 0.2112 | 0.0000 | 0.0153 | 0.2670 |
| projector_only | 0.2772 | 0.2375 | 0.2465 | 0.0000 | 0.0410 | 0.3300 |
| llm_only | 0.3515 | 0.3598 | 0.3760 | 0.0343 | -0.0327 | 0.4300 |
| llm_projector | 0.3490 | 0.3548 | 0.3765 | 0.0367 | -0.0367 | 0.4410 |

## Final Scores by Task

| Mode | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| vision_only | 0.2220 | 0.2210 | 0.1810 | 0.2670 |
| projector_only | 0.2820 | 0.2600 | 0.2370 | 0.3300 |
| llm_only | 0.3400 | 0.3250 | 0.3110 | 0.4300 |
| llm_projector | 0.3230 | 0.3320 | 0.3000 | 0.4410 |

## Forgetting by Task

| Mode | Task | At learning | Best after learning | Final | Forgetting | Final - learning |
|---|---|---:|---:|---:|---:|---:|
| vision_only | single_evidence | 0.2030 | 0.2220 | 0.2220 | 0.0000 | 0.0190 |
| vision_only | multi_evidence | 0.1980 | 0.2210 | 0.2210 | 0.0000 | 0.0230 |
| vision_only | cross_region_or_multihop | 0.1770 | 0.1810 | 0.1810 | 0.0000 | 0.0040 |
| vision_only | cross_context | 0.2670 | 0.2670 | 0.2670 | 0.0000 | 0.0000 |
| projector_only | single_evidence | 0.2230 | 0.2820 | 0.2820 | 0.0000 | 0.0590 |
| projector_only | multi_evidence | 0.2260 | 0.2600 | 0.2600 | 0.0000 | 0.0340 |
| projector_only | cross_region_or_multihop | 0.2070 | 0.2370 | 0.2370 | 0.0000 | 0.0300 |
| projector_only | cross_context | 0.3300 | 0.3300 | 0.3300 | 0.0000 | 0.0000 |
| llm_only | single_evidence | 0.4040 | 0.4040 | 0.3400 | 0.0640 | -0.0640 |
| llm_only | multi_evidence | 0.3640 | 0.3640 | 0.3250 | 0.0390 | -0.0390 |
| llm_only | cross_region_or_multihop | 0.3060 | 0.3110 | 0.3110 | 0.0000 | 0.0050 |
| llm_only | cross_context | 0.4300 | 0.4300 | 0.4300 | 0.0000 | 0.0000 |
| llm_projector | single_evidence | 0.3910 | 0.3910 | 0.3230 | 0.0680 | -0.0680 |
| llm_projector | multi_evidence | 0.3500 | 0.3500 | 0.3320 | 0.0180 | -0.0180 |
| llm_projector | cross_region_or_multihop | 0.3240 | 0.3240 | 0.3000 | 0.0240 | -0.0240 |
| llm_projector | cross_context | 0.4410 | 0.4410 | 0.4410 | 0.0000 | 0.0000 |
