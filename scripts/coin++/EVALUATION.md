# CoIN++ Dataset-Native Evaluation

The original `eval_factor1_llava_json.py` inference files are preserved. The
new evaluator rescoring those predictions writes:

```text
<result-root>/<stage>/predictions_official/<task>.jsonl
<result-root>/<stage>/metrics_official_all.json
<result-root>/summary_official/
```

## Metric Routing

| Source dataset | Primary metric |
|---|---|
| VQAv2, TextVQA, OK-VQA | official VQA soft accuracy over 10 human answers |
| DocVQA, InfographicVQA | ANLS |
| ChartQA, ChartQA-eval, current TQA alias | ChartQA relaxed accuracy |
| AI2D, A-OKVQA, ICON-QA, MMMU, Visual7W | multiple-choice accuracy |
| TallyQA | normalized count accuracy |
| GQA, DVQA, Geometry3K, PathVQA, SLAKE, VQA-RAD | benchmark-style normalized accuracy |
| Unregistered dataset or missing required annotations | LLM correctness judge |

The output reports both the micro average over factor samples and the macro
average over source datasets. It also records official-metric and LLM-Judge
coverage, so fallback use is visible rather than silently mixed into the score.

## Rescore One Factor

Start an OpenAI-compatible judge endpoint only if the manifest reports samples
that cannot be scored by a native metric. The defaults match the local Qwen
service used by the metadata pipeline:

```bash
JUDGE_MODEL=qwen3.6 \
JUDGE_BASE_URL=http://127.0.0.1:8001/v1 \
FACTOR=evidence_complexity \
bash scripts/coin++/run_official_judge_eval.sh
```

Rescore a completed Skill or Visual experiment by overriding the result root:

```bash
FACTOR=skill_requirement \
RESULT_ROOTS=results/coin++/skill_requirement/eval \
bash scripts/coin++/run_official_judge_eval.sh
```

Use `JUDGE_MODE=off ALLOW_UNSCORED=1` only to debug metric routing without an
API. Such output is not suitable for reporting if `unscored_count` is nonzero.

## Rescore Trainable-Module Results

```bash
bash scripts/coin++/run_trainable_modules_official_judge_eval.sh
```

The three default regimes are rescored without repeating model inference. Their
new comparison is written to:

```text
results/coin++_trainable_modules/visual_substrate/comparison_official/module_comparison.md
```

## Reproducibility

The first run builds a compact annotation cache at:

```text
cl_dataset/coin_factor1_final/evaluation_annotations.jsonl
```

Keep this file with the final benchmark release. LLM-Judge decisions are
cached under `results/coin++/judge_cache/`, and each scored prediction records
the judge model, prompt version, fallback reason, and short decision rationale.
