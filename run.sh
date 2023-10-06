python evaluate.py --by_letter --load_8bit --base_model='bigscience/bloomz-560m' --lora_weights='x'
python evaluate.py --by_letter --load_8bit --base_model='bigscience/bloomz-1b1' --lora_weights='x'
python evaluate.py --by_letter --load_8bit --base_model='bigscience/bloomz-1b7' --lora_weights='x'
python evaluate.py --by_letter --load_8bit --base_model='bigscience/bloomz-3b' --lora_weights='x'
python evaluate.py --by_letter --load_8bit --base_model='bigscience/bloomz-7b1' --lora_weights='x'

python evaluate.py --by_letter --load_8bit --base_model='facebook/xglm-564M' --lora_weights='x'
python evaluate.py --by_letter --load_8bit --base_model='facebook/xglm-1.7B' --lora_weights='x'
python evaluate.py --by_letter --load_8bit --base_model='facebook/xglm-2.9B' --lora_weights='x'
python evaluate.py --by_letter --load_8bit --base_model='facebook/xglm-4.5B' --lora_weights='x'
python evaluate.py --by_letter --load_8bit --base_model='facebook/xglm-7.5B' --lora_weights='x'

python evaluate_falcon.py --by_letter --load_8bit --base_model='tiiuae/falcon-7b' --lora_weights='x'
python evaluate_falcon.py --by_letter --load_8bit --base_model='tiiuae/falcon-7b-instruct' --lora_weights='x'
python evaluate_falcon.py --by_letter --load_8bit --base_model='tiiuae/falcon-40b' --lora_weights='x'
python evaluate_falcon.py --by_letter --load_8bit --base_model='tiiuae/falcon-40b-instruct' --lora_weights='x'

python evaluate_mt0.py --by_letter --load_8bit --base_model='bigscience/mt0-small' --lora_weights='x'
python evaluate_mt0.py --by_letter --load_8bit --base_model='bigscience/mt0-base' --lora_weights='x'
python evaluate_mt0.py --by_letter --load_8bit --base_model='bigscience/mt0-large' --lora_weights='x'
python evaluate_mt0.py --by_letter --load_8bit --base_model='bigscience/mt0-xl' --lora_weights='x'
python evaluate_mt0.py --by_letter --load_8bit --base_model='bigscience/mt0-xxl' --lora_weights='x'

python evaluate_llama.py --by_letter --base_model='decapoda-research/llama-7b-hf' --lora_weights='x'
python evaluate_llama.py --by_letter --base_model='decapoda-research/llama-13b-hf' --lora_weights='x'
python evaluate_llama.py --by_letter --base_model='decapoda-research/llama-30b-hf' --lora_weights='x'

python evaluate_bactrian.py --by_letter --load_8bit --base_model='decapoda-research/llama-7b-hf' --lora_weights='MBZUAI/bactrian-x-llama-7b-lora'
python evaluate_bactrian.py --by_letter --load_8bit --base_model='decapoda-research/llama-13b-hf' --lora_weights='MBZUAI/bactrian-x-llama-13b-lora'
