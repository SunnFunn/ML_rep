FROM python:3.9.1

RUN apt-get clean && apt-get update

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser surnames;echo 'surnames:1234567890' | chpasswd
USER surnames

WORKDIR /app
COPY --chown=surnames:surnames . .
RUN chown -R surnames:surnames .

EXPOSE 5000
CMD ["uwsgi", "surnames.ini"]
