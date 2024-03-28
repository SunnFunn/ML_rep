FROM python:3.9.1
WORKDIR /app
COPY . .
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT [ "python3", "run.py"]