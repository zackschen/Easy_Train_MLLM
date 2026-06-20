# #!/bin/bash

# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/1_eval_sqa.sh Finetune ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/ScienceQA_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/2_eval_textqa.sh Finetune ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/TextVQA_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/3_eval_ImageNet.sh Finetune ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/ImageNet_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/4_eval_gqa.sh Finetune ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/GQA_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/5_eval_vizwiz.sh Finetune ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/VizWiz_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/6_eval_grounding.sh Finetune ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/Grounding_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/7_eval_vqav2.sh Finetune ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/VQAv2_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/8_eval_ocrvqa.sh Finetune ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/OCRVQA_llava_lora

# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/1_eval_sqa.sh TextVQA ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/TextVQA_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/1_eval_sqa.sh ImageNet ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/ImageNet_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/1_eval_sqa.sh GQA ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/GQA_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/1_eval_sqa.sh VizWiz ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/VizWiz_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/1_eval_sqa.sh Grounding ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/Grounding_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/1_eval_sqa.sh VQAv2 ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/VQAv2_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/1_eval_sqa.sh OCRVQA ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/OCRVQA_llava_lora

# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/2_eval_textqa.sh ImageNet ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/ImageNet_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/2_eval_textqa.sh GQA ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/GQA_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/2_eval_textqa.sh VizWiz ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/VizWiz_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/2_eval_textqa.sh Grounding ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/Grounding_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/2_eval_textqa.sh VQAv2 ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/VQAv2_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/2_eval_textqa.sh OCRVQA ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/OCRVQA_llava_lora

# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/3_eval_ImageNet.sh GQA ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/GQA_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/3_eval_ImageNet.sh VizWiz ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/VizWiz_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/3_eval_ImageNet.sh Grounding ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/Grounding_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/3_eval_ImageNet.sh VQAv2 ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/VQAv2_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/3_eval_ImageNet.sh OCRVQA ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/OCRVQA_llava_lora

# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/4_eval_gqa.sh VizWiz ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/VizWiz_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/4_eval_gqa.sh Grounding ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/Grounding_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/4_eval_gqa.sh VQAv2 ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/VQAv2_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/4_eval_gqa.sh OCRVQA ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/OCRVQA_llava_lora

CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/5_eval_vizwiz.sh Grounding ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/Grounding_llava_lora
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/5_eval_vizwiz.sh VQAv2 ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/VQAv2_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/5_eval_vizwiz.sh OCRVQA ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/OCRVQA_llava_lora

# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/6_eval_grounding.sh VQAv2 ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/VQAv2_llava_lora
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/6_eval_grounding.sh OCRVQA ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/OCRVQA_llava_lora

# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash ./scripts/LLaVA/COIN/Eval_0.4_MOE/7_eval_vqav2.sh OCRVQA ./checkpoints/LLaVA/Instruction/CoIN_0_4_MOE/OCRVQA_llava_lora
