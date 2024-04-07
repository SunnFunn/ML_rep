FROM python:3.9.1

RUN apt-get clean && apt-get update

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser sentiments;echo 'sentiments:1234567890' | chpasswd
USER sentiments

WORKDIR /app
COPY --chown=sentiments:sentiments . .
RUN chown -R sentiments:sentiments .

EXPOSE 5000
CMD ["uwsgi", "sentiments.ini"]
