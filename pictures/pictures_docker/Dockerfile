FROM python:3.9.1
WORKDIR /usr/src/app
COPY ./src/ .
COPY requirements.txt ./
RUN apt update && apt upgrade -y
RUN pip install --upgrade pip
RUN apt-get install -y poppler-utils
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
ENTRYPOINT ["streamlit","run","./run.py"]
