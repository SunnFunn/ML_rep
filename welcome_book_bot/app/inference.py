import faiss
import numpy as np
import json

from app import Data
from app.embedding import embed

from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'


with open('./app/context_source/wb.json', 'r', encoding='utf-8') as file:
    wb = json.load(file)


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

    dists, idxs = index.search(query, Data.k_neighbors)

    context = wb[str(idxs[0][0])]
    output = chain.invoke({"input": text, "context": context})

    return output


#if __name__ == '__main__':
#    text = 'Какие столовые  есть в комбинате питания ПАО «НЕФАЗ»?'
#    print(response(text))
