import faiss
import numpy as np
import pickle

from app import Data
from app.embedding import embed

from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'


with open('./app/context_source/wb.pkl', 'rb') as file:
    docs = pickle.load(file)
with open('./app/context_source/wb_chunks.pkl', 'rb') as file:
    chunks = pickle.load(file)


index = faiss.read_index('./app/faiss_index/flat_wb.index')
llm = Ollama(model="llama3")
output_parser = StrOutputParser()
prompt_template = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input} Ответь на русском языке""")
chain = prompt_template | llm | output_parser


def response(text):
    query = np.random.random((1, Data.emb_dimension)).astype('float32')
    query[0] = embed(text).detach().numpy()
    faiss.normalize_L2(query)

    _, idxs = index.search(query, Data.k_neighbors)

    context = ''
    pages = []
    keys_list = [k for k, v in chunks.items()]
    for idx in idxs[0]:
        page_number = docs[idx].metadata['page']
        if page_number not in keys_list:
            page_number = list(filter(lambda x: x < page_number, keys_list))[-1]
        if page_number not in pages:
            pages.append(page_number)
            context += chunks[page_number]

    output = chain.invoke({"input": text, "context": context})

    return output
