# Skill Requirement Trainable-Module Comparison (relaxed_match)

## Overall Continual Metrics

| Mode | Final average | Mean seen accuracy | Mean at learning | Avg forgetting (old) | BWT (old) | Final-task score |
|---|---:|---:|---:|---:|---:|---:|
| vision_only | 0.2616 | 0.2351 | 0.2309 | 0.0092 | 0.0341 | 0.4400 |
| projector_only | 0.2974 | 0.3019 | 0.2992 | 0.0191 | -0.0020 | 0.4810 |
| llm_only | 0.3569 | 0.4095 | 0.3901 | 0.0424 | -0.0369 | 0.5550 |

## Final Scores by Task

| Mode | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| vision_only | 0.3570 | 0.2240 | 0.2610 | 0.2890 | 0.0960 | 0.1380 | 0.3110 | 0.1310 | 0.3690 | 0.4400 |
| projector_only | 0.4400 | 0.2400 | 0.2660 | 0.3440 | 0.1290 | 0.1620 | 0.3470 | 0.1540 | 0.4110 | 0.4810 |
| llm_only | 0.5060 | 0.2940 | 0.3980 | 0.3880 | 0.1810 | 0.1950 | 0.3600 | 0.2590 | 0.4330 | 0.5550 |

## Forgetting by Task

| Mode | Task | At learning | Best after learning | Final | Forgetting | Final - learning |
|---|---|---:|---:|---:|---:|---:|
| vision_only | recognition | 0.2850 | 0.3570 | 0.3570 | 0.0000 | 0.0720 |
| vision_only | counting | 0.1420 | 0.2240 | 0.2240 | 0.0000 | 0.0820 |
| vision_only | medical_reasoning | 0.2920 | 0.2940 | 0.2610 | 0.0330 | -0.0310 |
| vision_only | knowledge_reasoning | 0.2230 | 0.2890 | 0.2890 | 0.0000 | 0.0660 |
| vision_only | chart_reasoning | 0.1370 | 0.1460 | 0.0960 | 0.0500 | -0.0410 |
| vision_only | document_reasoning | 0.1020 | 0.1380 | 0.1380 | 0.0000 | 0.0360 |
| vision_only | text_reading | 0.2410 | 0.3110 | 0.3110 | 0.0000 | 0.0700 |
| vision_only | diagram_reasoning | 0.1240 | 0.1310 | 0.1310 | 0.0000 | 0.0070 |
| vision_only | relation | 0.3230 | 0.3690 | 0.3690 | 0.0000 | 0.0460 |
| vision_only | attribute | 0.4400 | 0.4400 | 0.4400 | 0.0000 | 0.0000 |
| projector_only | recognition | 0.3470 | 0.4420 | 0.4400 | 0.0020 | 0.0930 |
| projector_only | counting | 0.2790 | 0.2800 | 0.2400 | 0.0400 | -0.0390 |
| projector_only | medical_reasoning | 0.3060 | 0.3060 | 0.2660 | 0.0400 | -0.0400 |
| projector_only | knowledge_reasoning | 0.3630 | 0.3660 | 0.3440 | 0.0220 | -0.0190 |
| projector_only | chart_reasoning | 0.1680 | 0.1680 | 0.1290 | 0.0390 | -0.0390 |
| projector_only | document_reasoning | 0.1340 | 0.1620 | 0.1620 | 0.0000 | 0.0280 |
| projector_only | text_reading | 0.3380 | 0.3610 | 0.3470 | 0.0140 | 0.0090 |
| projector_only | diagram_reasoning | 0.1500 | 0.1540 | 0.1540 | 0.0000 | 0.0040 |
| projector_only | relation | 0.4260 | 0.4260 | 0.4110 | 0.0150 | -0.0150 |
| projector_only | attribute | 0.4810 | 0.4810 | 0.4810 | 0.0000 | 0.0000 |
| llm_only | recognition | 0.5810 | 0.5810 | 0.5060 | 0.0750 | -0.0750 |
| llm_only | counting | 0.3530 | 0.3560 | 0.2940 | 0.0620 | -0.0590 |
| llm_only | medical_reasoning | 0.4300 | 0.4390 | 0.3980 | 0.0410 | -0.0320 |
| llm_only | knowledge_reasoning | 0.4580 | 0.4580 | 0.3880 | 0.0700 | -0.0700 |
| llm_only | chart_reasoning | 0.2500 | 0.2590 | 0.1810 | 0.0780 | -0.0690 |
| llm_only | document_reasoning | 0.1720 | 0.1950 | 0.1950 | 0.0000 | 0.0230 |
| llm_only | text_reading | 0.3830 | 0.3890 | 0.3600 | 0.0290 | -0.0230 |
| llm_only | diagram_reasoning | 0.2630 | 0.2630 | 0.2590 | 0.0040 | -0.0040 |
| llm_only | relation | 0.4560 | 0.4560 | 0.4330 | 0.0230 | -0.0230 |
| llm_only | attribute | 0.5550 | 0.5550 | 0.5550 | 0.0000 | 0.0000 |
