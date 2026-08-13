# Evidence Complexity Module Dual Evaluation

Standard and LLM-Judge results are reported independently; no fallback or hybrid score is used.

## Standard Continual Metrics

| Mode | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| vision_only | 0.1657 | 0.1089 | 0.1117 | 0.0000 | 0.0721 |
| projector_only | 0.2611 | 0.2518 | 0.2507 | 0.0024 | 0.0139 |
| llm_only | 0.3553 | 0.3713 | 0.3817 | 0.0352 | -0.0352 |
| llm_projector | 0.3522 | 0.3672 | 0.3834 | 0.0415 | -0.0415 |

### Standard Final Scores By Task

| Mode | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| vision_only | 0.1827 | 0.1566 | 0.1411 | 0.1826 |
| projector_only | 0.2866 | 0.2317 | 0.2273 | 0.2986 |
| llm_only | 0.3637 | 0.3287 | 0.2961 | 0.4328 |
| llm_projector | 0.3583 | 0.3210 | 0.2820 | 0.4476 |

## LLM Judge Continual Metrics

| Mode | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |
|---|---:|---:|---:|---:|---:|
| vision_only | 0.2491 | 0.2447 | 0.2397 | 0.0026 | 0.0125 |
| projector_only | 0.2864 | 0.2773 | 0.2867 | 0.0060 | -0.0005 |
| llm_only | 0.3755 | 0.3819 | 0.4012 | 0.0343 | -0.0343 |
| llm_projector | 0.3716 | 0.3756 | 0.3969 | 0.0337 | -0.0337 |

### LLM Judge Final Scores By Task

| Mode | single_evidence | multi_evidence | cross_region_or_multihop | cross_context |
|---|---:|---:|---:|---:|
| vision_only | 0.2688 | 0.2451 | 0.1828 | 0.2998 |
| projector_only | 0.2996 | 0.2557 | 0.2258 | 0.3644 |
| llm_only | 0.3754 | 0.3474 | 0.3043 | 0.4747 |
| llm_projector | 0.3643 | 0.3491 | 0.2899 | 0.4831 |

## Per-Task Forgetting

| Track | Mode | Task | At learning | Best | Final | Forgetting | BWT |
|---|---|---|---:|---:|---:|---:|---:|
| standard | vision_only | single_evidence | 0.0729 | 0.1827 | 0.1827 | 0.0000 | 0.1098 |
| standard | vision_only | multi_evidence | 0.0785 | 0.1566 | 0.1566 | 0.0000 | 0.0782 |
| standard | vision_only | cross_region_or_multihop | 0.1128 | 0.1411 | 0.1411 | 0.0000 | 0.0283 |
| standard | vision_only | cross_context | 0.1826 | 0.1826 | 0.1826 | 0.0000 | 0.0000 |
| standard | projector_only | single_evidence | 0.2485 | 0.2866 | 0.2866 | 0.0000 | 0.0381 |
| standard | projector_only | multi_evidence | 0.2389 | 0.2389 | 0.2317 | 0.0073 | -0.0073 |
| standard | projector_only | cross_region_or_multihop | 0.2166 | 0.2273 | 0.2273 | 0.0000 | 0.0107 |
| standard | projector_only | cross_context | 0.2986 | 0.2986 | 0.2986 | 0.0000 | 0.0000 |
| standard | llm_only | single_evidence | 0.4381 | 0.4381 | 0.3637 | 0.0745 | -0.0745 |
| standard | llm_only | multi_evidence | 0.3598 | 0.3598 | 0.3287 | 0.0311 | -0.0311 |
| standard | llm_only | cross_region_or_multihop | 0.2961 | 0.2961 | 0.2961 | 0.0000 | 0.0001 |
| standard | llm_only | cross_context | 0.4328 | 0.4328 | 0.4328 | 0.0000 | 0.0000 |
| standard | llm_projector | single_evidence | 0.4268 | 0.4268 | 0.3583 | 0.0685 | -0.0685 |
| standard | llm_projector | multi_evidence | 0.3502 | 0.3502 | 0.3210 | 0.0292 | -0.0292 |
| standard | llm_projector | cross_region_or_multihop | 0.3089 | 0.3089 | 0.2820 | 0.0269 | -0.0269 |
| standard | llm_projector | cross_context | 0.4476 | 0.4476 | 0.4476 | 0.0000 | 0.0000 |
| llm_judge | vision_only | single_evidence | 0.2438 | 0.2724 | 0.2688 | 0.0036 | 0.0250 |
| llm_judge | vision_only | multi_evidence | 0.2317 | 0.2483 | 0.2451 | 0.0032 | 0.0134 |
| llm_judge | vision_only | cross_region_or_multihop | 0.1837 | 0.1837 | 0.1828 | 0.0009 | -0.0009 |
| llm_judge | vision_only | cross_context | 0.2998 | 0.2998 | 0.2998 | 0.0000 | 0.0000 |
| llm_judge | projector_only | single_evidence | 0.2872 | 0.2996 | 0.2996 | 0.0000 | 0.0124 |
| llm_judge | projector_only | multi_evidence | 0.2737 | 0.2737 | 0.2557 | 0.0180 | -0.0180 |
| llm_judge | projector_only | cross_region_or_multihop | 0.2216 | 0.2258 | 0.2258 | 0.0000 | 0.0042 |
| llm_judge | projector_only | cross_context | 0.3644 | 0.3644 | 0.3644 | 0.0000 | 0.0000 |
| llm_judge | llm_only | single_evidence | 0.4396 | 0.4396 | 0.3754 | 0.0642 | -0.0642 |
| llm_judge | llm_only | multi_evidence | 0.3809 | 0.3809 | 0.3474 | 0.0335 | -0.0335 |
| llm_judge | llm_only | cross_region_or_multihop | 0.3094 | 0.3094 | 0.3043 | 0.0051 | -0.0051 |
| llm_judge | llm_only | cross_context | 0.4747 | 0.4747 | 0.4747 | 0.0000 | 0.0000 |
| llm_judge | llm_projector | single_evidence | 0.4232 | 0.4232 | 0.3643 | 0.0589 | -0.0589 |
| llm_judge | llm_projector | multi_evidence | 0.3669 | 0.3669 | 0.3491 | 0.0178 | -0.0178 |
| llm_judge | llm_projector | cross_region_or_multihop | 0.3143 | 0.3143 | 0.2899 | 0.0244 | -0.0244 |
| llm_judge | llm_projector | cross_context | 0.4831 | 0.4831 | 0.4831 | 0.0000 | 0.0000 |
