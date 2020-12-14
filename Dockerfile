FROM python:3.6-alpine

RUN adduser -D e-library

WORKDIR /home/e-library

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY e-library.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP e-library.py

RUN chown -R e-library:e-library ./
USER e-library

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]