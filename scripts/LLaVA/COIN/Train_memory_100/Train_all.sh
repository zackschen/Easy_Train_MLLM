#!/bin/bash

sh ./scripts/LLaVA/COIN/Train_memory_100/1_Science.sh
sh ./scripts/LLaVA/COIN/Train_memory_100/2_TextVQA.sh
sh ./scripts/LLaVA/COIN/Train_memory_100/3_ImageNet.sh
sh ./scripts/LLaVA/COIN/Train_memory_100/4_GQA.sh
sh ./scripts/LLaVA/COIN/Train_memory_100/5_VizWiz.sh
sh ./scripts/LLaVA/COIN/Train_memory_100/6_Grounding.sh
sh ./scripts/LLaVA/COIN/Train_memory_100/7_vqav2.sh
sh ./scripts/LLaVA/COIN/Train_memory_100/8_OCRVQA.sh

sh ./scripts/LLaVA/COIN/Eval_memory_100/eval_Trained.sh