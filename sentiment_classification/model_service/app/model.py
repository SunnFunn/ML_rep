import torch
from torch import Tensor
import torch.nn as nn
import torch.utils.data

import numpy as np
import math
import json


class Vocabulary(object):
    """Class to process text and extract vocabulary for mapping"""

    def __init__(self, token_to_idx=None):
        if token_to_idx is None:
            token_to_idx = {}
        self._token_to_idx = token_to_idx

        self._idx_to_token = {idx: token
                              for token, idx in self._token_to_idx.items()}

    def to_serializable(self):
        return {'token_to_idx': self._token_to_idx}

    @classmethod
    def from_serializable(cls, contents):
        return cls(**contents)

    def add_token(self, token):
        if token in self._token_to_idx:
            index = self._token_to_idx[token]
        else:
            index = len(self._token_to_idx)
            self._token_to_idx[token] = index
            self._idx_to_token[index] = token
        return index

    def add_many(self, tokens):
        return [self.add_token(token) for token in tokens]

    def lookup_token(self, token):
        return self._token_to_idx[token]

    def lookup_index(self, index):
        if index not in self._idx_to_token:
            raise KeyError("the index (%d) is not in the Vocabulary" % index)
        return self._idx_to_token[index]

    def __str__(self):
        return "<Vocabulary(size=%d)>" % len(self)

    def __len__(self):
        return len(self._token_to_idx)


class SequenceVocabulary(Vocabulary):
    def __init__(self, token_to_idx=None, unk_token="<UNK>",
                 mask_token="<MASK>", begin_seq_token="<BEGIN>",
                 end_seq_token="<END>"):

        super(SequenceVocabulary, self).__init__(token_to_idx)

        self._mask_token = mask_token
        self._unk_token = unk_token
        self._begin_seq_token = begin_seq_token
        self._end_seq_token = end_seq_token

        self.mask_index = self.add_token(self._mask_token)
        self.unk_index = self.add_token(self._unk_token)
        self.begin_seq_index = self.add_token(self._begin_seq_token)
        self.end_seq_index = self.add_token(self._end_seq_token)

    def to_serializable(self):
        contents = super(SequenceVocabulary, self).to_serializable()
        contents.update({'unk_token': self._unk_token,
                         'mask_token': self._mask_token,
                         'begin_seq_token': self._begin_seq_token,
                         'end_seq_token': self._end_seq_token})
        return contents

    def lookup_token(self, token):
        if self.unk_index >= 0:
            return self._token_to_idx.get(token, self.unk_index)
        else:
            return self._token_to_idx[token]


class NMTVectorizer(object):
    """ The Vectorizer which coordinates the Vocabularies and puts them to use"""

    def __init__(self, vocab, category_vocab, max_text_length):

        self.vocab = vocab
        self.category_vocab = category_vocab
        self.max_text_length = max_text_length

    def _vectorize(self, indices, vector_length=-1, mask_index=0):
        if vector_length < 0:
            vector_length = len(indices)

        vector = np.zeros(vector_length, dtype=np.int64)
        vector[:len(indices)] = indices
        vector[len(indices):] = mask_index

        return vector

    def _get_source_indices(self, text):
        indices = []
        indices.extend(self.vocab.lookup_token(token) for token in text.split(" "))
        return indices

    def vectorize(self, text, use_dataset_max_lengths=True):

        source_vector_length = -1

        if use_dataset_max_lengths:
            source_vector_length = self.max_text_length

        source_indices = self._get_source_indices(text)
        source_vector = self._vectorize(source_indices,
                                        vector_length=source_vector_length,
                                        mask_index=self.vocab.mask_index)

        return {"source_vector": source_vector,
                "source_length": len(source_indices)}


    @classmethod
    def from_serializable(cls, contents):
        vocab = SequenceVocabulary.from_serializable(contents["vocab"])
        category_vocab = Vocabulary.from_serializable(contents['category_vocab'])

        return cls(vocab=vocab, category_vocab=category_vocab,
                   max_text_length=contents["max_text_length"])


def load_vectorizer(vectorizer_filepath):
    with open(vectorizer_filepath) as fp:
        return NMTVectorizer.from_serializable(json.load(fp))


class PositionalEncoding(nn.Module):

    def __init__(self, d_model: int, dropout: float = 0.25, max_length: int = 17):
        super().__init__()

        self.dropout = nn.Dropout(p=dropout)

        position = torch.arange(max_length).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_length, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x: Tensor) -> Tensor:
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)


def create_mask(src, padding_idx=0):
    batch_size = src.size(0)
    src_seq_len = src.size(1)

    src_mask = torch.zeros((src_seq_len, src_seq_len), device='cpu').expand(batch_size, -1, -1).type(torch.bool)
    src_mask = torch.cat([src_mask, src_mask, src_mask,
                          src_mask, src_mask, src_mask], dim=0)

    src_padding_mask = (src == padding_idx)
    return src_mask, src_padding_mask


class NMTDecoder(nn.Module):
    def __init__(self, num_embeddings, embedding_size,
                 max_len_target,
                 pretrained_embeddings=None):

        super(NMTDecoder, self).__init__()

        self.max_len_target = max_len_target
        self.embedding_size = embedding_size

        self.pe = PositionalEncoding(d_model=embedding_size, max_length=max_len_target)

        if pretrained_embeddings is None:
            self.target_embedding = nn.Embedding(num_embeddings, embedding_size, padding_idx=0)

        else:
            self.target_embedding = nn.Embedding(num_embeddings, embedding_size, padding_idx=0,
                                                 _weight=pretrained_embeddings)

        self.multihead_attn = nn.MultiheadAttention(embedding_size, num_heads=6, dropout=0.35)
        self.ff = nn.Sequential(
            nn.Linear(embedding_size, 4 * embedding_size),
            nn.ReLU(),
            nn.Dropout(0.35),
            nn.Linear(4 * embedding_size, embedding_size))
        self.norm = nn.BatchNorm1d(max_len_target)
        self.classifier = nn.Sequential(nn.Linear(embedding_size, 6), nn.ReLU(), nn.Dropout(0.35))

    def forward(self, x_source, src_padding_mask, src_mask):

        # создаем вложения слов и их позиций(эмбеддинги)
        embedded = self.target_embedding(x_source).permute(1, 0, 2)
        pe_embedded = self.pe.forward(embedded)
        attn_in = pe_embedded

        # блок расчета самовнимания
        x = self.multihead_attn(attn_in, attn_in, attn_in,
                                key_padding_mask=src_padding_mask,
                                attn_mask=src_mask)[0].permute(1, 0, 2)
        attn_out_norm = self.norm(x + attn_in.permute(1, 0, 2))
        x = self.ff(attn_out_norm)
        x = self.norm(x + attn_out_norm)

        # блок классификации
        scores = self.classifier(x)
        scores = torch.sum(scores, dim=1) / self.max_len_target

        return scores


class NMTModel(nn.Module):
    """ The Neural Machine Translation Model """

    def __init__(self, target_vocab_size, target_embedding_size,
                 max_length, pretrained_embeddings=None):
        super(NMTModel, self).__init__()

        self.decoder = NMTDecoder(num_embeddings=target_vocab_size,
                                  embedding_size=target_embedding_size,
                                  max_len_target=max_length,
                                  pretrained_embeddings=pretrained_embeddings)

    def forward(self, x_source, src_padding_mask, src_mask):
        decoded_states = self.decoder(x_source,
                                      src_padding_mask=src_padding_mask,
                                      src_mask=src_mask)

        return decoded_states


vectorizer = load_vectorizer('./app/model/vectorizer.json')

classifier = NMTModel(target_vocab_size=len(vectorizer.vocab),
                      target_embedding_size=300,
                      max_length=vectorizer.max_text_length,
                      pretrained_embeddings=None)
