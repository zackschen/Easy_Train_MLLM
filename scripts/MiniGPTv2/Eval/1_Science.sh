RESULT_DIR="./results/CoIN_New/MiniGPTv2/ScienceQA"
MODELPATH=$2

deepspeed --include localhost:0,1,2,3,4,5,6,7 \
    ETrain/Eval/MiniGPT/model_vqa.py \
    --cfg-path ./scripts/MiniGPTv2/Eval/1_Science.yaml \
    --image-folder ./cl_dataset \
    --model-path $MODELPATH \
    --answers-file $RESULT_DIR/$1/merge.jsonl \

output_file=$RESULT_DIR/$1/merge.jsonl

python -m ETrain.Eval.LLaVA.CoIN.eval_science_qa \
    --base-dir ./cl_dataset/ScienceQA \
    --result-file $output_file \
    --output-file $RESULT_DIR/$1/output.jsonl \
    --output-result $RESULT_DIR/$1/output_result.jsonl \

python -m ETrain.Eval.LLaVA.CoIN.create_prompt \
    --rule ./ETrain/Eval/LLaVA/CoIN/rule.json \
    --questions ./playground/Instructions_slim/ScienceQA/test.json \
    --results $output_file \