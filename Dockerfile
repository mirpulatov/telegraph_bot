FROM python:2.7-alpine

RUN apk update && apk upgrade
RUN apk add poppler-utils libxslt-dev build-base

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN pip install --upgrade setuptools

ADD . /app
WORKDIR /app

ENV PYTHONPATH $PYTHONPATH:/app/

CMD ["python", "/app/bot.py"]