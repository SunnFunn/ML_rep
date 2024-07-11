import fitz
import re
import json
from collections import defaultdict
import codecs

doc = fitz.open('./context_source/wb.pdf')
page_counts = doc.page_count

text = []
for page in range(4, page_counts - 1):
    for b in doc[page].get_text('blocks'):
        cleaned_text = re.sub(r"[^0-9а-яА-Я., \-\№]", '', b[4]).strip()
        cleaned_text.encode('utf-8').decode('utf-8')
        text.append(cleaned_text)

text_no_spaces = []
for block in text:
    if not (not block or block.isspace()):
        text_no_spaces.append(block)

headers = []
for block in text_no_spaces:
    if block.isupper():
        headers.append(block)

headers_idxs = [i for i, v in enumerate(text_no_spaces) if v.isupper()]
wb_chunks = [" ".join(text_no_spaces[i:j]) for i, j in zip(headers_idxs[:-1], headers_idxs[1:])]

wb_dict = defaultdict(list)
for idx, chunk in enumerate(wb_chunks):
    wb_dict[idx] = chunk

if __name__ == '__main__':
    with open('./context_source/wb.json', 'w', encoding='cp1251') as json_file:
        json.dump(wb_dict, json_file, ensure_ascii=False)

    with codecs.open('./context_source/wb.json', 'r', encoding='cp1251') as f:
        content = f.read()
    with codecs.open('./context_source/wb.json', 'w', encoding='utf-8') as f:
        f.write(content)
