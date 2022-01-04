FROM python:3.8
WORKDIR /usr/src/app
COPY ./src/ .
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install sklearn
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
ENTRYPOINT ["streamlit","run","./heart.py"]
