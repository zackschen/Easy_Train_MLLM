#!/usr/bin/env bash
set -euo pipefail

# Rescore existing CoIN++ predictions without rerunning LLaVA inference.
# Dataset-native metrics are used first; only annotation-incomplete or unknown
# samples are sent to an OpenAI-compatible LLM judge.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
cd "$PROJECT_ROOT"

if [[ -x /root/miniconda3/envs/ETrain/bin/python ]]; then
  DEFAULT_PYTHON=/root/miniconda3/envs/ETrain/bin/python
else
  DEFAULT_PYTHON=python3
fi
PYTHON_BIN="${PYTHON_BIN:-$DEFAULT_PYTHON}"
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"

FACTOR="${FACTOR:-evidence_complexity}"
DATA_ROOT="${DATA_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_final}"
ORDER_JSON="${ORDER_JSON:-$DATA_ROOT/splits/$FACTOR/transition_order.json}"
RESULT_ROOTS="${RESULT_ROOTS:-$PROJECT_ROOT/results/coin++/$FACTOR/eval}"

SCORER="${SCORER:-$PROJECT_ROOT/scripts/evaluate_coinpp_predictions.py}"
SUMMARIZER="${SUMMARIZER:-$PROJECT_ROOT/scripts/summarize_coinpp_official_eval.py}"
ANNOTATION_CACHE="${ANNOTATION_CACHE:-$DATA_ROOT/evaluation_annotations.jsonl}"
JUDGE_CACHE="${JUDGE_CACHE:-$PROJECT_ROOT/results/coin++/judge_cache/${FACTOR}.jsonl}"

JUDGE_MODE="${JUDGE_MODE:-fallback}"
JUDGE_MODEL="${JUDGE_MODEL:-qwen3.6}"
JUDGE_BASE_URL="${JUDGE_BASE_URL:-${OPENAI_BASE_URL:-http://127.0.0.1:8001/v1}}"
JUDGE_API_KEY="${JUDGE_API_KEY:-${OPENAI_API_KEY:-EMPTY}}"
JUDGE_BATCH_SIZE="${JUDGE_BATCH_SIZE:-8}"
JUDGE_TIMEOUT="${JUDGE_TIMEOUT:-180}"
JUDGE_RETRIES="${JUDGE_RETRIES:-3}"
LIMIT="${LIMIT:-}"
SKIP_COMPLETED="${SKIP_COMPLETED:-0}"
ALLOW_UNSCORED="${ALLOW_UNSCORED:-0}"

for required in "$ORDER_JSON" "$SCORER" "$SUMMARIZER"; do
  if [[ ! -e "$required" ]]; then
    echo "Missing required path: $required" >&2
    exit 1
  fi
done

read -r -a result_roots <<< "$RESULT_ROOTS"
if [[ "${#result_roots[@]}" -eq 0 ]]; then
  echo "RESULT_ROOTS is empty" >&2
  exit 1
fi
for root in "${result_roots[@]}"; do
  if [[ ! -d "$root" ]]; then
    echo "Missing result root: $root" >&2
    exit 1
  fi
done

result_args=()
for root in "${result_roots[@]}"; do
  result_args+=(--result-root "$root")
done

metadata_args=()
if [[ -n "${METADATA_JSONLS:-}" ]]; then
  read -r -a metadata_paths <<< "$METADATA_JSONLS"
  for path in "${metadata_paths[@]}"; do
    metadata_args+=(--metadata-jsonl "$path")
  done
fi

optional_args=()
if [[ -n "$LIMIT" ]]; then
  optional_args+=(--limit "$LIMIT")
fi
if [[ "$SKIP_COMPLETED" == "1" ]]; then
  optional_args+=(--skip-completed)
fi
if [[ "$ALLOW_UNSCORED" == "1" ]]; then
  optional_args+=(--allow-unscored)
fi

cat <<EOF
CoIN++ dataset-native + LLM-Judge evaluation
  factor:            $FACTOR
  result roots:      ${result_roots[*]}
  order:             $ORDER_JSON
  Python:            $PYTHON_BIN
  annotation cache:  $ANNOTATION_CACHE
  judge mode:        $JUDGE_MODE
  judge model:       $JUDGE_MODEL
  judge API:         $JUDGE_BASE_URL
  judge cache:       $JUDGE_CACHE
  sample limit:      ${LIMIT:-all}
EOF

"$PYTHON_BIN" "$SCORER" \
  --project-root "$PROJECT_ROOT" \
  --annotation-cache "$ANNOTATION_CACHE" \
  --judge-mode "$JUDGE_MODE" \
  --judge-model "$JUDGE_MODEL" \
  --judge-base-url "$JUDGE_BASE_URL" \
  --judge-api-key "$JUDGE_API_KEY" \
  --judge-cache "$JUDGE_CACHE" \
  --judge-batch-size "$JUDGE_BATCH_SIZE" \
  --judge-timeout "$JUDGE_TIMEOUT" \
  --judge-retries "$JUDGE_RETRIES" \
  "${result_args[@]}" \
  "${metadata_args[@]}" \
  "${optional_args[@]}"

for root in "${result_roots[@]}"; do
  "$PYTHON_BIN" "$SUMMARIZER" \
    --result-root "$root" \
    --order-json "$ORDER_JSON" \
    --factor-name "$FACTOR" \
    --metric primary_score
done

echo
echo "Rescoring completed."
for root in "${result_roots[@]}"; do
  echo "  $root/summary_official/learning_matrix.md"
done
