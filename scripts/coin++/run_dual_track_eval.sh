#!/usr/bin/env bash
set -euo pipefail

# Rescore saved CoIN++ predictions with two independent tracks:
#   1. source-benchmark metric, or normalized direct comparison
#   2. CoIN-style 0-10 LLM Judge for every prediction

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
DATA_ROOT="${DATA_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_final_textvqa_clean}"
ORDER_JSON="${ORDER_JSON:-$DATA_ROOT/splits/$FACTOR/transition_order.json}"
RESULT_ROOTS="${RESULT_ROOTS:-$PROJECT_ROOT/results/coin++_textvqa_clean/$FACTOR/eval}"

SCORER="${SCORER:-$PROJECT_ROOT/scripts/evaluate_coinpp_dual.py}"
SUMMARIZER="${SUMMARIZER:-$PROJECT_ROOT/scripts/summarize_coinpp_dual_eval.py}"
case "$FACTOR" in
  evidence_complexity)
    DEFAULT_ANNOTATION_CACHE="$DATA_ROOT/evaluation_annotations_evidence.jsonl"
    ;;
  skill_requirement)
    DEFAULT_ANNOTATION_CACHE="$DATA_ROOT/evaluation_annotations_skill.jsonl"
    ;;
  visual_substrate)
    DEFAULT_ANNOTATION_CACHE="$DATA_ROOT/evaluation_annotations_visual.jsonl"
    ;;
  *)
    DEFAULT_ANNOTATION_CACHE="$DATA_ROOT/evaluation_annotations_${FACTOR}.jsonl"
    ;;
esac
ANNOTATION_CACHE="${ANNOTATION_CACHE:-$DEFAULT_ANNOTATION_CACHE}"

JUDGE_MODEL="${JUDGE_MODEL:-qwen3.6}"
JUDGE_BASE_URL="${JUDGE_BASE_URL:-${OPENAI_BASE_URL:-http://127.0.0.1:8001/v1}}"
JUDGE_API_KEY="${JUDGE_API_KEY:-${OPENAI_API_KEY:-EMPTY}}"
JUDGE_BATCH_SIZE="${JUDGE_BATCH_SIZE:-1}"
JUDGE_WORKERS="${JUDGE_WORKERS:-4}"
JUDGE_TIMEOUT="${JUDGE_TIMEOUT:-180}"
JUDGE_RETRIES="${JUDGE_RETRIES:-3}"
SAFE_JUDGE_MODEL="${JUDGE_MODEL//\//_}"
JUDGE_CACHE="${JUDGE_CACHE:-$PROJECT_ROOT/results/coin++_textvqa_clean/judge_cache/${FACTOR}_${SAFE_JUDGE_MODEL}_all.jsonl}"

LIMIT="${LIMIT:-}"
SKIP_COMPLETED="${SKIP_COMPLETED:-0}"
ALLOW_MISSING_REFERENCE="${ALLOW_MISSING_REFERENCE:-0}"

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
if [[ "$ALLOW_MISSING_REFERENCE" == "1" ]]; then
  optional_args+=(--allow-missing-reference)
fi

cat <<EOF
CoIN++ independent standard + all-sample LLM-Judge evaluation
  factor:            $FACTOR
  result roots:      ${result_roots[*]}
  order:             $ORDER_JSON
  Python:            $PYTHON_BIN
  annotation cache:  $ANNOTATION_CACHE
  standard track:    official/registered metric, then direct comparison
  judge coverage:    every prediction
  judge model:       $JUDGE_MODEL
  judge API:         $JUDGE_BASE_URL
  judge cache:       $JUDGE_CACHE
  judge request:     CoIN scalar, one sample per request
  judge workers:     $JUDGE_WORKERS
  sample limit:      ${LIMIT:-all}
EOF

"$PYTHON_BIN" "$SCORER" \
  --project-root "$PROJECT_ROOT" \
  --annotation-cache "$ANNOTATION_CACHE" \
  --judge-model "$JUDGE_MODEL" \
  --judge-base-url "$JUDGE_BASE_URL" \
  --judge-api-key "$JUDGE_API_KEY" \
  --judge-cache "$JUDGE_CACHE" \
  --judge-batch-size "$JUDGE_BATCH_SIZE" \
  --judge-workers "$JUDGE_WORKERS" \
  --judge-timeout "$JUDGE_TIMEOUT" \
  --judge-retries "$JUDGE_RETRIES" \
  "${result_args[@]}" \
  "${metadata_args[@]}" \
  "${optional_args[@]}"

for root in "${result_roots[@]}"; do
  "$PYTHON_BIN" "$SUMMARIZER" \
    --result-root "$root" \
    --order-json "$ORDER_JSON" \
    --factor-name "$FACTOR"
done

echo
echo "Dual-track evaluation completed."
for root in "${result_roots[@]}"; do
  echo "  $root/summary_dual/learning_matrices.md"
done
