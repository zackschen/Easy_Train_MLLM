#!/bin/bash

# sh ./scripts/LLaVA/COIN/Train_rank256/1_Science.sh
# sh ./scripts/LLaVA/COIN/Train_rank256/2_TextVQA.sh
sh ./scripts/LLaVA/COIN/Train_rank256/3_ImageNet.sh
sh ./scripts/LLaVA/COIN/Train_rank256/4_GQA.sh
sh ./scripts/LLaVA/COIN/Train_rank256/5_VizWiz.sh
sh ./scripts/LLaVA/COIN/Train_rank256/6_Grounding.sh
sh ./scripts/LLaVA/COIN/Train_rank256/7_vqav2.sh
sh ./scripts/LLaVA/COIN/Train_rank256/8_OCRVQA.sh

sh ./scripts/LLaVA/COIN/Train_rank192/Train_all.sh