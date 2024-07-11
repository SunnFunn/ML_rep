import torch
from transformers import AutoTokenizer, AutoModel

from app import Data


model = AutoModel.from_pretrained(Data.emb_model_name)
tokenizer = AutoTokenizer.from_pretrained(Data.emb_model_name)
max_length = Data.max_length


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    return sum_embeddings / sum_mask


def embed(text_input):
    encoded_input = tokenizer(text_input, padding=True, truncation=True, max_length=max_length, return_tensors='pt')
    with torch.no_grad():
        output = model(**encoded_input)
    embeddings = mean_pooling(output, encoded_input['attention_mask'])

    return embeddings[0]
