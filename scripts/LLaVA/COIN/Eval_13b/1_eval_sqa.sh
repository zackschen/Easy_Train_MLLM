#!/bin/bash

gpu_list="${CUDA_VISIBLE_DEVICES:-0}"
IFS=',' read -ra GPULIST <<< "$gpu_list"

CHUNKS=${#GPULIST[@]}

if [ ! -n "$1" ] ;then
    STAGE='Finetune'
else
    STAGE=$1
fi

if [ ! -n "$2" ] ;then
    MODELPATH='./checkpoints/Instruction/Only_Pretrain_1.5/ScienceQA/llava-1.5-7b-lora'
else
    MODELPATH=$2
fi

RESULT_DIR="./results/CoIN/LLaVA-13B/ScienceQA"

deepspeed --include localhost:0,1,2,3,4,5,6,7 \
    ETrain/Eval/LLaVA/model_vqa.py \
    --model-path $MODELPATH \
    --model-base ./checkpoints/LLaVA/Vicuna/vicuna-13b-v1.5 \
    --question-file ./playground/Instructions_slim/ScienceQA/test.json \
    --image-folder ./cl_dataset \
    --answers-file $RESULT_DIR/$STAGE/merge.jsonl \
    --temperature 0 \
    --conv-mode vicuna_v1 &

wait

output_file=$RESULT_DIR/$STAGE/merge.jsonl


python -m ETrain.Eval.LLaVA.CoIN.eval_science_qa \
    --base-dir ./cl_dataset/ScienceQA \
    --result-file $output_file \
    --output-file $RESULT_DIR/$STAGE/output.jsonl \
    --output-result $RESULT_DIR/$STAGE/output_result.jsonl \

python -m ETrain.Eval.LLaVA.CoIN.create_prompt \
    --rule ./ETrain/Eval/LLaVA/CoIN/rule.json \
    --questions ./playground/Instructions_slim/ScienceQA/test.json \
    --results $output_file \