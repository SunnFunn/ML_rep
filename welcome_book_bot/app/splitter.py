from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pickle


loader = PyMuPDFLoader(file_path="context_source/wb.pdf")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=0,
    length_function=len,
)
documents = text_splitter.split_documents(docs[6:-1])

max_len = 0
for doc in documents:
    if max_len < len(doc.page_content.split(' ')):
        max_len = len(doc.page_content.split(' '))


if __name__ == '__main__':
    print(max_len)
    with open('./context_source/wb.pkl', 'wb') as file:
        pickle.dump(documents, file, protocol=pickle.HIGHEST_PROTOCOL)
