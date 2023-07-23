FROM python:3.9.1
WORKDIR /app
COPY . .
RUN apt-get clean && RUN apt-get update
RUN apt-get install -y poppler-utils
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
ENTRYPOINT ["streamlit","run","./run.py"]
