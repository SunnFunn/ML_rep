FROM python:3.9.1
WORKDIR /app
COPY . .
RUN apt-get clean && apt-get update
RUN apt-get install -y poppler-utils
RUN pip install --upgrade pip
RUN pip3 install opencv-python == 4.8.0
RUN pip3 install torchvision == 0.16.0+cpu
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
ENTRYPOINT ["streamlit","run","./run.py"]
