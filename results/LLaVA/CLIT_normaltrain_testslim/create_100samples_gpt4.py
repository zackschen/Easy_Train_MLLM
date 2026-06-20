import json
import numpy as np
import os
import argparse

def eval_model(args):
    # open json
    path = args.eval_path
    datas = json.load(open(path))

    sample_size = 100
    train_choice = np.random.choice(len(datas),sample_size,replace=False)
    chose_samples = [datas[i][-1]['content'] for i in train_choice]

    path = path.replace('CLIT_normaltrain_testslim','To_Eval_GPT4')
    os.makedirs(os.path.split(path)[0],exist_ok=True)
    json.dump(chose_samples, open(path,'w'),indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-path", type=str, default="./results/LLaVA/CLIT_normaltrain_testslim/ScienceQA/Finetune/prompt_to_eval.json")
    args = parser.parse_args()
    eval_model(args)