import torch
import torch.nn.functional as F
import numpy as np


def softmax(x):
    z = x - max(x)
    numerator = np.exp(z)
    denominator = np.sum(numerator)
    softmax = numerator/denominator
    return softmax


@torch.no_grad()
def get_logprobs_causal(model, tokenizer, prompt, device):
    inputs = tokenizer(prompt, return_tensors="pt")
    if model.config.model_type == 'falcon':
        inputs.pop("token_type_ids")
    input_ids, output_ids = inputs["input_ids"].to(device), inputs["input_ids"][:, 1:].to(device)
    outputs = model(**inputs, labels=input_ids)

    logits = outputs.logits.to(torch.double).to(device)
    output_ids = output_ids.to(logits.get_device()) #in case of paralellism
    logprobs = torch.gather(F.log_softmax(logits, dim=2), 2, output_ids.unsqueeze(2))
    
    return logprobs.mean()

def predict_classification_causal(model, tokenizer, input_text, labels, device):
    probs = [get_logprobs_causal(model, tokenizer, input_text+label, device) for label in labels]
    return probs

def predict_classification_causal_by_letter(model, tokenizer, input_text, labels, device):
    choices = ['A', 'B', 'C', 'D', 'E'][:len(labels)]
    choice_ids = [tokenizer.encode(choice)[-1] for choice in choices]
    with torch.no_grad():
        inputs = tokenizer(input_text, return_tensors="pt")
        input_ids = inputs["input_ids"].to(device)
        if model.config.model_type == 'falcon':
            inputs.pop("token_type_ids")
        outputs = model(**inputs, labels=input_ids)
        last_token_logits = outputs.logits[:, -1, :]
        choice_logits = last_token_logits[:, choice_ids].detach().cpu().numpy()
        conf = softmax(choice_logits[0])
        pred = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E"}[np.argmax(choice_logits[0])]
    return conf, pred


@torch.no_grad()
def get_logprobs_mt0(model, tokenizer, prompt, device, label_ids=None, label_attn=None):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to('cuda')
    
    outputs = model(**inputs, decoder_input_ids=model._shift_right(label_ids))
    logits = outputs.logits

    logprobs = torch.gather(F.log_softmax(logits, dim=2), 2, label_ids.unsqueeze(2)) * label_attn.unsqueeze(2)
    return logprobs.sum() / label_attn.sum()

def predict_classification_mt0(model, tokenizer, input_text, labels, device):
    labels_encoded = tokenizer(labels, add_special_tokens=False, padding=True, return_tensors='pt')
    list_label_ids = labels_encoded['input_ids'].to('cuda')
    list_label_attn = labels_encoded['attention_mask'].to('cuda')
    probs = [
        get_logprobs_mt0(model, tokenizer, input_text, device, label_ids.view(1,-1), label_attn.view(1,-1)) 
          for (label_ids, label_attn) in zip(list_label_ids, list_label_attn)
    ]
    return probs

def predict_classification_mt0_by_letter(model, tokenizer, input_text, labels, device):
    choices = ['A', 'B', 'C', 'D', 'E'][:len(labels)]
    choice_ids = [tokenizer.encode(choice)[0] for choice in choices]
    with torch.no_grad():
        start_token = tokenizer('<pad>', return_tensors="pt").to(device)
        inputs = tokenizer(input_text, return_tensors="pt").to(device)
        outputs = model(**inputs, decoder_input_ids=start_token['input_ids'])
        last_token_logits = outputs.logits[:, -1, :]
        choice_logits = last_token_logits[:, choice_ids].detach().cpu().numpy()
        conf = softmax(choice_logits[0])
        pred = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E"}[np.argmax(choice_logits[0])]

    return conf, pred

