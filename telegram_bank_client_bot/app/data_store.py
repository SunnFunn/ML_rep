from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_progress import ProgressManager


loader = PyMuPDFLoader(file_path="faiss_index/client_manual.pdf")
text_splitter = RecursiveCharacterTextSplitter()
embeddings = OllamaEmbeddings(model='nomic-embed-text')
docs = loader.load()


def initialize_v_store(data):
    documents = text_splitter.split_documents(data)
    with ProgressManager(embeddings):
        vector = FAISS.from_documents(documents, embeddings)
    vector.save_local("faiss_index")


if __name__ == '__main__':
    initialize_v_store(docs)

