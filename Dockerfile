FROM python:3.8-slim-buster

ARG workers=2

ENV TINI_VERSION v0.18.0

RUN apt-get update -y && \
    apt-get install -y postgresql libpq-dev gcc && \
    pip install -U pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . /opt/app/

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini

RUN chmod +x /tini && \
    useradd --create-home appuser

# STOPSIGNAL SIGINT

USER appuser
ENTRYPOINT ["/tini", "-s", "--"]

WORKDIR /opt/app

EXPOSE 5000

CMD ["gunicorn", "-w ${workers}", "-b :5000", "server:APP"]
