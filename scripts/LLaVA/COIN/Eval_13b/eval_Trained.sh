# #!/bin/CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash

CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/1_eval_sqa.sh Finetune ./checkpoints/CoIN-13b/ScienceQA_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/2_eval_textqa.sh Finetune ./checkpoints/CoIN-13b/TextVQA_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/3_eval_ImageNet.sh Finetune ./checkpoints/CoIN-13b/ImageNet_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/4_eval_gqa.sh Finetune ./checkpoints/CoIN-13b/GQA_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/5_eval_vizwiz.sh Finetune ./checkpoints/CoIN-13b/VizWiz_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/6_eval_grounding.sh Finetune ./checkpoints/CoIN-13b/Grounding_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/7_eval_vqav2.sh Finetune ./checkpoints/CoIN-13b/VQAv2_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/8_eval_ocrvqa.sh Finetune ./checkpoints/CoIN-13b/OCRVQA_llava_lora

CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/1_eval_sqa.sh TextVQA ./checkpoints/CoIN-13b/TextVQA_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/1_eval_sqa.sh ImageNet ./checkpoints/CoIN-13b/ImageNet_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/1_eval_sqa.sh GQA ./checkpoints/CoIN-13b/GQA_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/1_eval_sqa.sh VizWiz ./checkpoints/CoIN-13b/VizWiz_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/1_eval_sqa.sh Grounding ./checkpoints/CoIN-13b/Grounding_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/1_eval_sqa.sh VQAv2 ./checkpoints/CoIN-13b/VQAv2_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/1_eval_sqa.sh OCRVQA ./checkpoints/CoIN-13b/OCRVQA_llava_lora

CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/2_eval_textqa.sh ImageNet ./checkpoints/CoIN-13b/ImageNet_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/2_eval_textqa.sh GQA ./checkpoints/CoIN-13b/GQA_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/2_eval_textqa.sh VizWiz ./checkpoints/CoIN-13b/VizWiz_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/2_eval_textqa.sh Grounding ./checkpoints/CoIN-13b/Grounding_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/2_eval_textqa.sh VQAv2 ./checkpoints/CoIN-13b/VQAv2_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/2_eval_textqa.sh OCRVQA ./checkpoints/CoIN-13b/OCRVQA_llava_lora

CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/3_eval_ImageNet.sh GQA ./checkpoints/CoIN-13b/GQA_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/3_eval_ImageNet.sh VizWiz ./checkpoints/CoIN-13b/VizWiz_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/3_eval_ImageNet.sh Grounding ./checkpoints/CoIN-13b/Grounding_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/3_eval_ImageNet.sh VQAv2 ./checkpoints/CoIN-13b/VQAv2_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/3_eval_ImageNet.sh OCRVQA ./checkpoints/CoIN-13b/OCRVQA_llava_lora

CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/4_eval_gqa.sh VizWiz ./checkpoints/CoIN-13b/VizWiz_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/4_eval_gqa.sh Grounding ./checkpoints/CoIN-13b/Grounding_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/4_eval_gqa.sh VQAv2 ./checkpoints/CoIN-13b/VQAv2_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/4_eval_gqa.sh OCRVQA ./checkpoints/CoIN-13b/OCRVQA_llava_lora

CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/5_eval_vizwiz.sh Grounding ./checkpoints/CoIN-13b/Grounding_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/5_eval_vizwiz.sh VQAv2 ./checkpoints/CoIN-13b/VQAv2_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/5_eval_vizwiz.sh OCRVQA ./checkpoints/CoIN-13b/OCRVQA_llava_lora

CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/6_eval_grounding.sh VQAv2 ./checkpoints/CoIN-13b/VQAv2_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/6_eval_grounding.sh OCRVQA ./checkpoints/CoIN-13b/OCRVQA_llava_lora

CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_13b/7_eval_vqav2.sh OCRVQA ./checkpoints/CoIN-13b/OCRVQA_llava_lora