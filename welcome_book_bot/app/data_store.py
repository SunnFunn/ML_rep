import faiss
import pickle
import re
from tqdm import tqdm as t
import numpy as np
from app import Data
from app.embedding import embed


with open('./context_source/wb.pkl', 'rb') as file:
    docs = pickle.load(file)

index = faiss.IndexFlatIP(Data.emb_dimension)
data_store = np.random.random((len(docs), Data.emb_dimension)).astype('float32')


def main():
    for idx, doc in t(enumerate(docs)):
        #text = doc.page_content
        text = re.sub(r"[^0-9а-яА-Я., \-\№]", '', doc.page_content).strip()
        data_store[idx] = embed(text).detach().numpy()

    faiss.normalize_L2(data_store)
    index.add(data_store)
    faiss.write_index(index, './faiss_index/flat_wb.index')


if __name__ == '__main__':
    main()

