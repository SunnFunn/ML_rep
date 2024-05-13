FROM python:3.9.1

RUN apt-get clean && apt-get update

RUN curl -fsSL https://ollama.com/install.sh | sh

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser pics;echo 'pics:1234567890' | chpasswd
USER pics

WORKDIR /app
COPY --chown=pics:pics . .
RUN chown -R pics:pics .

EXPOSE 5000
CMD ["uwsgi", "pics.ini"]
