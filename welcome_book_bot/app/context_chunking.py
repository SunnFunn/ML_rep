import fitz
import re
import pickle
from collections import defaultdict
import codecs

doc = fitz.open('./context_source/wb.pdf')
page_counts = doc.page_count

headers_pages = []

for page in range(7, page_counts - 1):
    for b in doc[page].get_text('blocks'):
        if b[4].isupper():
            headers_pages.append(page)

headers_pages = list(set(headers_pages))

text_dict = defaultdict(str)

for page in range(7, page_counts - 1):
    page_text = doc[page].get_text()
    if page in headers_pages:
        text_dict[page] = re.sub(r"[^0-9а-яА-Я., \-\№]", '', page_text).strip()
    else:
        nearest_page = list(filter(lambda x: x < page, headers_pages))[-1]
        text_dict[nearest_page] += re.sub(r"[^0-9а-яА-Я., \-\№]", '', page_text).strip()

if __name__ == '__main__':
    with open('./context_source/wb_chunks.pkl', 'wb') as file:
        pickle.dump(text_dict, file, protocol=pickle.HIGHEST_PROTOCOL)
    #with open('./context_source/wb.json', 'w', encoding='cp1251') as json_file:
    #    json.dump(wb_dict, json_file, ensure_ascii=False)

    #with codecs.open('./context_source/wb.json', 'r', encoding='cp1251') as f:
    #    content = f.read()
    #with codecs.open('./context_source/wb.json', 'w', encoding='utf-8') as f:
    #    f.write(content)
