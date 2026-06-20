#!/bin/bash

sh ./scripts/LLaVA/COIN/Train_0.4_MOE/1_Science.sh
sh ./scripts/LLaVA/COIN/Train_0.4_MOE/2_TextVQA.sh
sh ./scripts/LLaVA/COIN/Train_0.4_MOE/3_ImageNet.sh
sh ./scripts/LLaVA/COIN/Train_0.4_MOE/4_GQA.sh
sh ./scripts/LLaVA/COIN/Train_0.4_MOE/5_VizWiz.sh
sh ./scripts/LLaVA/COIN/Train_0.4_MOE/6_Grounding.sh
sh ./scripts/LLaVA/COIN/Train_0.4_MOE/7_vqav2.sh
sh ./scripts/LLaVA/COIN/Train_0.4_MOE/8_OCRVQA.sh

# sh ./scripts/LLaVA/COIN/Eval_memory_100/eval_Trained.sh
# sh ./scripts/LLaVA/COIN/Eval_0.4_MOE/eval_Trained.sh
