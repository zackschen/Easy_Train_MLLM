# CoIN++ Dual Evaluation

The canonical result protocol has two independent tracks for every saved
prediction:

1. `standard_score`: use the registered source-benchmark metric when its
   annotations are available; otherwise use normalized answer comparison.
2. `llm_judge_score`: send every prediction to an OpenAI-compatible Judge,
   following CoIN's 0-10 answer-quality scale. Reports normalize this value to
   `[0, 1]`, while scored JSONL files also retain `raw_score_0_10`.

The two scores are never merged into a fallback or hybrid score.

The Judge uses the versioned `rubric-scalar-v4` protocol. Each request contains
one sample, places the detailed correctness rubric in the system message, and
requires one numeric 0-10 response. The rubric defines semantic equivalence,
partial credit, contradictions, multiple references, exact numeric answers,
and prompt-injection resistance. Qwen requests explicitly disable thinking so
the response budget cannot be consumed by hidden reasoning. For the Judge
track only, TextVQA annotation-control responses are removed when semantic
human answers remain; the official TextVQA metric still receives all ten
original answers. If a scalar response is malformed, the evaluator retries
the same rubric with a JSON Schema constrained output and records the transport
as `json_schema_recovery`; this formatting recovery does not change the cache
key or invalidate successful scalar judgments. Changing the rubric changes the
cache key.

## Factor Evaluation

Start the Judge service, then run:

```bash
FACTOR=evidence_complexity \
JUDGE_MODEL=qwen3.6 \
JUDGE_BASE_URL=http://127.0.0.1:8001/v1 \
bash scripts/coin++/run_dual_track_eval.sh
```

Use `FACTOR=skill_requirement` or `FACTOR=visual_substrate` for the other
tracks. A completed run writes:

```text
<eval-root>/<stage>/predictions_dual/<task>.jsonl
<eval-root>/<stage>/metrics_dual_all.json
<eval-root>/summary_dual/learning_matrices.md
<eval-root>/summary_dual/matrix_standard_score.csv
<eval-root>/summary_dual/matrix_llm_judge_score.csv
```

Judge results are appended to `JUDGE_CACHE`. If a run is interrupted, rerun
the same command; cached predictions are skipped automatically.

For a small end-to-end check:

```bash
LIMIT=20 JUDGE_BATCH_SIZE=1 JUDGE_WORKERS=1 \
bash scripts/coin++/run_dual_track_eval.sh
```

Do not use a limited run as the final report because it writes limited
`metrics_dual_all.json` files.

## Trainable Modules

```bash
FACTOR=visual_substrate \
MODULE_MODES="vision_only projector_only llm_only" \
JUDGE_MODEL=qwen3.6 \
JUDGE_BASE_URL=http://127.0.0.1:8001/v1 \
bash scripts/coin++/run_trainable_modules_dual_eval.sh
```

The cross-module report is written to:

```text
results/coin++_trainable_modules/visual_substrate/comparison_dual/module_comparison_dual.md
```
