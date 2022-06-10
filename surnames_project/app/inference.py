import torch
import torch.nn as nn
import torch.utils.data
import torch.nn.functional as F
from app.model import classifier, vectorizer

def decode_samples(sampled_indices, vectorizer):
    decoded_surnames = []
    vocab = vectorizer.char_vocab
    
    for sample_index in range(sampled_indices.shape[0]):
        surname = ""
        for time_step in range(sampled_indices.shape[1]):
            sample_item = sampled_indices[sample_index, time_step].item()
            if sample_item == vocab.begin_seq_index:
                continue
            elif sample_item == vocab.end_seq_index:
                break
            else:
                surname += vocab.lookup_index(sample_item)
        decoded_surnames.append(surname)
    return decoded_surnames

def inference(input_text, temperature):
	nationality_index = torch.tensor(0, dtype=torch.int64).unsqueeze(dim=0)
	vocab = vectorizer.char_vocab
	
	indices_initial = [vectorizer.char_vocab.begin_seq_index]
	for char in input_text:
		indices_initial.append(vocab.lookup_token(char))
	indices_initial = torch.tensor(indices_initial, dtype=torch.int64).unsqueeze(dim=0)
	indices = indices_initial
	
	for i in range(len(input_text), 20):
		h_t = None
		x_t = indices
		x_emb_t = classifier.char_emb(x_t)
		nationality_embedded = classifier.nation_emb(nationality_index).unsqueeze(0)
		rnn_out_t, h_t = classifier.rnn(x_emb_t,nationality_embedded)
		prediction_vector = classifier.fc(rnn_out_t.squeeze(dim=0))
		probability_vector = F.softmax(prediction_vector/temperature, dim=1)
		max_value_index = torch.multinomial(probability_vector[i], num_samples=1).unsqueeze(0)
		indices = torch.cat([x_t, max_value_index], dim=1)
	return indices
