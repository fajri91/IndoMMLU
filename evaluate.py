import argparse
import sys
import pandas as pd
import math
import os
from peft import PeftModel
from transformers import LlamaForCausalLM, LlamaTokenizer, AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM 
from tqdm import tqdm
from numpy import argmax
import torch
from sklearn.metrics import accuracy_score

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"


def get_prompt(args):
    PROMPT = 'Ini adalah soal [SUBJECT] untuk [LEVEL]. Pilihlah salah satu jawaban yang dianggap benar!\n\n[INPUT]\n[OPTION]\n\nJawaban: '
    if args.lora_weights != "x":
        PROMPT = '### Input:\nIni adalah soal [SUBJECT] untuk [LEVEL]. Pilihlah salah satu jawaban yang dianggap benar!\n\n[INPUT]\n[OPTION]\n\nJawaban: ### Output:\n'
    return PROMPT


def prepare_data(prompt):
    inputs = []
    outputs = []
    outputs_options = []
    key2id = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
    data = pd.read_csv('data/indoMMLU.csv')
    for idx, row in data.iterrows():
        if row['level'] == 'Seleksi PTN':
            level = 'seleksi masuk universitas'
        else:
            try:
                level = f"{math.trunc(float(row['kelas']))} {row['level']}"
            except:
                level = f"{row['kelas']} {row['level']}"

        inputs.append(
            prompt.replace('[SUBJECT]', row['subject']).\
                   replace('[LEVEL]', level).\
                   replace('[INPUT]', row['soal']).\
                   replace('[OPTION]',row['jawaban'])
        )
        idx_label = key2id[row['kunci']]
        outputs.append(idx_label)
        outputs_options.append(row['jawaban'].split('\n'))
    return inputs, outputs, outputs_options


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--load_8bit", action='store_true')
    parser.add_argument("--share_gradio", action='store_true')
    parser.add_argument("--by_letter", action='store_true')
    parser.add_argument("--base_model", type=str, help="Path to pretrained model", required=True)
    parser.add_argument("--lora_weights", type=str, default="x")
    parser.add_argument("--output_folder", type=str, default="output", required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    os.makedirs(args.output_folder, exist_ok=True)
    
    tokenizer_class = LlamaTokenizer if 'llama' in args.base_model else AutoTokenizer
    model_class = LlamaForCausalLM if 'llama' in args.base_model else AutoModelForCausalLM

    SAVE_FILE = '{args.output_folder}/result_{args.base_model.split("/")[-1]}_{args.by_letter}.csv'
    tokenizer = tokenizer_class.from_pretrained(args.base_model)
    
    if 'mt0' in args.base_model:
        model = AutoModelForSeq2SeqLM.from_pretrained(args.base_model, device_map="auto", load_in_8bit="xxl" in args.base_model)
        from utils import predict_classification_mt0 as predict_classification
        from utils import predict_classification_mt0_by_letter as predict_classification_by_letter
    else:
        model = model_class.from_pretrained(args.base_model, load_in_8bit=args.load_8bit, torch_dtype=torch.float16, trust_remote_code=True, device_map="auto")
        from utils import predict_classification_causal as predict_classification
        from utils import predict_classification_causal_by_letter as predict_classification_by_letter
    
    # Load adapter if we use adapter
    if args.lora_weights != "x":
        model = PeftModel.from_pretrained(
            model,
            args.lora_weights,
            torch_dtype=torch.float16,
        )
        SAVE_FILE = '{args.output_folder}/result_{args.lora_weight.split("/")[-1]}_{args.by_letter}.csv'

    # unwind broken decapoda-research config
    if 'llama' in args.base_model:
        model.config.pad_token_id = tokenizer.pad_token_id = 0  # unk
        model.config.bos_token_id = 1
        model.config.eos_token_id = 2

    model.eval()
    if torch.__version__ >= "2" and sys.platform != "win32":
        model = torch.compile(model)
    
    
    prompt = get_prompt(args)
    inputs, golds, outputs_options = prepare_data(prompt)
    preds = []
    probs = []
    for idx in tqdm(range(len(inputs))):
        if not args.by_letter:
            out = predict_classification(model, tokenizer, inputs[idx], outputs_options[idx], device)
            prob = [o.cpu().detach().item() for o in out]
            pred = argmax(prob)
            preds.append(pred)
            probs.append(prob)
        else:
            conf, pred = predict_classification_by_letter(model, tokenizer, inputs[idx], outputs_options[idx], device)
            probs.append(conf)
            preds.append(pred)

    output_df = pd.DataFrame()
    output_df['input'] = inputs
    output_df['golds'] = golds
    output_df['options'] = outputs_options
    output_df['preds'] = preds
    output_df['probs'] = probs
    output_df.to_csv(SAVE_FILE, index=False)

if __name__ == "__main__":
    main()
