import faiss
import json
from tqdm import tqdm as t
import numpy as np
from app import Data
from app.embedding import embed


with open('./context_source/wb.json', 'r', encoding='utf-8') as file:
    wb = json.load(file)

index = faiss.IndexFlatIP(Data.emb_dimension)
data_store = np.random.random((len(wb), Data.emb_dimension)).astype('float32')


def main():
    for k, v in t(wb.items()):
        data_store[int(k)] = embed(v).detach().numpy()

    faiss.normalize_L2(data_store)
    index.add(data_store)
    faiss.write_index(index, './faiss_index/flat_wb.index')


if __name__ == '__main__':
    main()

