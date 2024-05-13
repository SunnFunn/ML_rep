from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

llm = Ollama(model="llama3")
output_parser = StrOutputParser()
embeddings = OllamaEmbeddings(model='nomic-embed-text')


prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")

document_chain = create_stuff_documents_chain(llm, prompt)
vectors = FAISS.load_local("app/faiss_index", embeddings, allow_dangerous_deserialization=True)


retriever = vectors.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)


def response(text):
    output = retrieval_chain.invoke({"input": text})['answer']
    return output




