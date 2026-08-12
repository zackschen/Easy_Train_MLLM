# Factor-1 Skill Requirement Continual Evaluation (relaxed_match)

## Performance Matrix

| Trained until | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recognition | 0.347 | 0.215 | 0.277 | 0.256 | 0.047 | 0.101 | 0.251 | 0.119 | 0.331 | 0.347 |
| counting | 0.374 | 0.279 | 0.292 | 0.278 | 0.089 | 0.133 | 0.276 | 0.108 | 0.349 | 0.381 |
| medical_reasoning | 0.391 | 0.255 | 0.306 | 0.317 | 0.079 | 0.113 | 0.275 | 0.115 | 0.350 | 0.406 |
| knowledge_reasoning | 0.438 | 0.257 | 0.266 | 0.363 | 0.075 | 0.152 | 0.319 | 0.134 | 0.401 | 0.445 |
| chart_reasoning | 0.437 | 0.258 | 0.285 | 0.354 | 0.168 | 0.137 | 0.305 | 0.137 | 0.367 | 0.419 |
| document_reasoning | 0.423 | 0.280 | 0.283 | 0.338 | 0.165 | 0.134 | 0.308 | 0.143 | 0.381 | 0.410 |
| text_reading | 0.441 | 0.269 | 0.271 | 0.360 | 0.163 | 0.144 | 0.338 | 0.143 | 0.406 | 0.441 |
| diagram_reasoning | 0.440 | 0.274 | 0.286 | 0.366 | 0.099 | 0.148 | 0.352 | 0.150 | 0.396 | 0.438 |
| relation | 0.442 | 0.251 | 0.260 | 0.352 | 0.130 | 0.153 | 0.361 | 0.148 | 0.426 | 0.457 |
| attribute | 0.440 | 0.240 | 0.266 | 0.344 | 0.129 | 0.162 | 0.347 | 0.154 | 0.411 | 0.481 |

## Forgetting

| Task | Score at learning | Best after learning | Final score | Forgetting |
|---|---:|---:|---:|---:|
| recognition | 0.347000 | 0.442000 | 0.440000 | 0.002000 |
| counting | 0.279000 | 0.280000 | 0.240000 | 0.040000 |
| medical_reasoning | 0.306000 | 0.306000 | 0.266000 | 0.040000 |
| knowledge_reasoning | 0.363000 | 0.366000 | 0.344000 | 0.022000 |
| chart_reasoning | 0.168000 | 0.168000 | 0.129000 | 0.039000 |
| document_reasoning | 0.134000 | 0.162000 | 0.162000 | 0.000000 |
| text_reading | 0.338000 | 0.361000 | 0.347000 | 0.014000 |
| diagram_reasoning | 0.150000 | 0.154000 | 0.154000 | 0.000000 |
| relation | 0.426000 | 0.426000 | 0.411000 | 0.015000 |
| attribute | 0.481000 | 0.481000 | 0.481000 | 0.000000 |
