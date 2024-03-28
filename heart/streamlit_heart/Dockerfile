FROM python:3.9.1

RUN pip install --upgrade pip
RUN pip install -U scikit-learn

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501
ENTRYPOINT ["streamlit","run","./heart.py"]
