FROM python:3.8-alpine
WORKDIR /app
COPY ./app/ .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000/tcp
ENTRYPOINT [ "python", "./sentiment.py"]