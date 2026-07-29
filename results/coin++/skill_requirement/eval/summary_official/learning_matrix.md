# CoIN++ Skill Requirement Evaluation

Primary metric: `primary_score`. Final average: **0.2243**; average forgetting on old tasks: **0.0773**; BWT: **-0.0773**.

## Continual Matrix

| Trained until | recognition | counting | medical_reasoning | knowledge_reasoning | chart_reasoning | document_reasoning | text_reading | diagram_reasoning | relation | attribute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| recognition | 0.5553 | 0.0970 | 0.2720 | 0.3468 | 0.1278 | 0.1624 | 0.2507 | 0.1691 | 0.3896 | 0.4101 |
| counting | 0.2551 | 0.2545 | 0.1940 | 0.2261 | 0.0648 | 0.0646 | 0.0734 | 0.1131 | 0.2651 | 0.3202 |
| medical_reasoning | 0.2726 | 0.2249 | 0.3680 | 0.2813 | 0.0969 | 0.0967 | 0.0976 | 0.1490 | 0.2560 | 0.3009 |
| knowledge_reasoning | 0.2703 | 0.2127 | 0.3370 | 0.3463 | 0.1133 | 0.0997 | 0.1175 | 0.1622 | 0.2730 | 0.3543 |
| chart_reasoning | 0.2220 | 0.2141 | 0.3400 | 0.3297 | 0.1858 | 0.1106 | 0.1319 | 0.0985 | 0.2431 | 0.2890 |
| document_reasoning | 0.2276 | 0.2367 | 0.3430 | 0.3035 | 0.1613 | 0.1535 | 0.1196 | 0.1114 | 0.2180 | 0.2892 |
| text_reading | 0.2485 | 0.1633 | 0.2950 | 0.3204 | 0.1434 | 0.1476 | 0.1476 | 0.1435 | 0.2514 | 0.3252 |
| diagram_reasoning | 0.2688 | 0.2248 | 0.3500 | 0.3231 | 0.1277 | 0.1289 | 0.1437 | 0.2172 | 0.2482 | 0.3409 |
| relation | 0.2575 | 0.2044 | 0.2840 | 0.2896 | 0.1113 | 0.1177 | 0.1274 | 0.1748 | 0.3319 | 0.3310 |
| attribute | 0.2667 | 0.2190 | 0.3000 | 0.2910 | 0.1181 | 0.1002 | 0.1058 | 0.1659 | 0.2973 | 0.3790 |

## Forgetting

| Task | At learning | Best after learning | Final | Forgetting | BWT |
|---|---:|---:|---:|---:|---:|
| recognition | 0.5553 | 0.5553 | 0.2667 | 0.2886 | -0.2886 |
| counting | 0.2545 | 0.2545 | 0.2190 | 0.0355 | -0.0355 |
| medical_reasoning | 0.3680 | 0.3680 | 0.3000 | 0.0680 | -0.0680 |
| knowledge_reasoning | 0.3463 | 0.3463 | 0.2910 | 0.0553 | -0.0553 |
| chart_reasoning | 0.1858 | 0.1858 | 0.1181 | 0.0677 | -0.0677 |
| document_reasoning | 0.1535 | 0.1535 | 0.1002 | 0.0533 | -0.0533 |
| text_reading | 0.1476 | 0.1476 | 0.1058 | 0.0418 | -0.0418 |
| diagram_reasoning | 0.2172 | 0.2172 | 0.1659 | 0.0513 | -0.0513 |
| relation | 0.3319 | 0.3319 | 0.2973 | 0.0346 | -0.0346 |
| attribute | 0.3790 | 0.3790 | 0.3790 | 0.0000 | 0.0000 |

## Scoring Coverage

| Trained until | Task | Official metric | LLM judge |
|---|---|---:|---:|
| recognition | recognition | 100.0% | 0.0% |
| recognition | counting | 100.0% | 0.0% |
| recognition | medical_reasoning | 100.0% | 0.0% |
| recognition | knowledge_reasoning | 100.0% | 0.0% |
| recognition | chart_reasoning | 100.0% | 0.0% |
| recognition | document_reasoning | 100.0% | 0.0% |
| recognition | text_reading | 100.0% | 0.0% |
| recognition | diagram_reasoning | 100.0% | 0.0% |
| recognition | relation | 100.0% | 0.0% |
| recognition | attribute | 100.0% | 0.0% |
| counting | recognition | 100.0% | 0.0% |
| counting | counting | 100.0% | 0.0% |
| counting | medical_reasoning | 100.0% | 0.0% |
| counting | knowledge_reasoning | 100.0% | 0.0% |
| counting | chart_reasoning | 100.0% | 0.0% |
| counting | document_reasoning | 100.0% | 0.0% |
| counting | text_reading | 100.0% | 0.0% |
| counting | diagram_reasoning | 100.0% | 0.0% |
| counting | relation | 100.0% | 0.0% |
| counting | attribute | 100.0% | 0.0% |
| medical_reasoning | recognition | 100.0% | 0.0% |
| medical_reasoning | counting | 100.0% | 0.0% |
| medical_reasoning | medical_reasoning | 100.0% | 0.0% |
| medical_reasoning | knowledge_reasoning | 100.0% | 0.0% |
| medical_reasoning | chart_reasoning | 100.0% | 0.0% |
| medical_reasoning | document_reasoning | 100.0% | 0.0% |
| medical_reasoning | text_reading | 100.0% | 0.0% |
| medical_reasoning | diagram_reasoning | 100.0% | 0.0% |
| medical_reasoning | relation | 100.0% | 0.0% |
| medical_reasoning | attribute | 100.0% | 0.0% |
| knowledge_reasoning | recognition | 100.0% | 0.0% |
| knowledge_reasoning | counting | 100.0% | 0.0% |
| knowledge_reasoning | medical_reasoning | 100.0% | 0.0% |
| knowledge_reasoning | knowledge_reasoning | 100.0% | 0.0% |
| knowledge_reasoning | chart_reasoning | 100.0% | 0.0% |
| knowledge_reasoning | document_reasoning | 100.0% | 0.0% |
| knowledge_reasoning | text_reading | 100.0% | 0.0% |
| knowledge_reasoning | diagram_reasoning | 100.0% | 0.0% |
| knowledge_reasoning | relation | 100.0% | 0.0% |
| knowledge_reasoning | attribute | 100.0% | 0.0% |
| chart_reasoning | recognition | 100.0% | 0.0% |
| chart_reasoning | counting | 100.0% | 0.0% |
| chart_reasoning | medical_reasoning | 100.0% | 0.0% |
| chart_reasoning | knowledge_reasoning | 100.0% | 0.0% |
| chart_reasoning | chart_reasoning | 100.0% | 0.0% |
| chart_reasoning | document_reasoning | 100.0% | 0.0% |
| chart_reasoning | text_reading | 100.0% | 0.0% |
| chart_reasoning | diagram_reasoning | 100.0% | 0.0% |
| chart_reasoning | relation | 100.0% | 0.0% |
| chart_reasoning | attribute | 100.0% | 0.0% |
| document_reasoning | recognition | 100.0% | 0.0% |
| document_reasoning | counting | 100.0% | 0.0% |
| document_reasoning | medical_reasoning | 100.0% | 0.0% |
| document_reasoning | knowledge_reasoning | 100.0% | 0.0% |
| document_reasoning | chart_reasoning | 100.0% | 0.0% |
| document_reasoning | document_reasoning | 100.0% | 0.0% |
| document_reasoning | text_reading | 100.0% | 0.0% |
| document_reasoning | diagram_reasoning | 100.0% | 0.0% |
| document_reasoning | relation | 100.0% | 0.0% |
| document_reasoning | attribute | 100.0% | 0.0% |
| text_reading | recognition | 100.0% | 0.0% |
| text_reading | counting | 100.0% | 0.0% |
| text_reading | medical_reasoning | 100.0% | 0.0% |
| text_reading | knowledge_reasoning | 100.0% | 0.0% |
| text_reading | chart_reasoning | 100.0% | 0.0% |
| text_reading | document_reasoning | 100.0% | 0.0% |
| text_reading | text_reading | 100.0% | 0.0% |
| text_reading | diagram_reasoning | 100.0% | 0.0% |
| text_reading | relation | 100.0% | 0.0% |
| text_reading | attribute | 100.0% | 0.0% |
| diagram_reasoning | recognition | 100.0% | 0.0% |
| diagram_reasoning | counting | 100.0% | 0.0% |
| diagram_reasoning | medical_reasoning | 100.0% | 0.0% |
| diagram_reasoning | knowledge_reasoning | 100.0% | 0.0% |
| diagram_reasoning | chart_reasoning | 100.0% | 0.0% |
| diagram_reasoning | document_reasoning | 100.0% | 0.0% |
| diagram_reasoning | text_reading | 100.0% | 0.0% |
| diagram_reasoning | diagram_reasoning | 100.0% | 0.0% |
| diagram_reasoning | relation | 100.0% | 0.0% |
| diagram_reasoning | attribute | 100.0% | 0.0% |
| relation | recognition | 100.0% | 0.0% |
| relation | counting | 100.0% | 0.0% |
| relation | medical_reasoning | 100.0% | 0.0% |
| relation | knowledge_reasoning | 100.0% | 0.0% |
| relation | chart_reasoning | 100.0% | 0.0% |
| relation | document_reasoning | 100.0% | 0.0% |
| relation | text_reading | 100.0% | 0.0% |
| relation | diagram_reasoning | 100.0% | 0.0% |
| relation | relation | 100.0% | 0.0% |
| relation | attribute | 100.0% | 0.0% |
| attribute | recognition | 100.0% | 0.0% |
| attribute | counting | 100.0% | 0.0% |
| attribute | medical_reasoning | 100.0% | 0.0% |
| attribute | knowledge_reasoning | 100.0% | 0.0% |
| attribute | chart_reasoning | 100.0% | 0.0% |
| attribute | document_reasoning | 100.0% | 0.0% |
| attribute | text_reading | 100.0% | 0.0% |
| attribute | diagram_reasoning | 100.0% | 0.0% |
| attribute | relation | 100.0% | 0.0% |
| attribute | attribute | 100.0% | 0.0% |
