FROM python:3.9.1
WORKDIR /usr/src/
COPY ./src/ .
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
ENTRYPOINT ["streamlit","run","./heart.py"]