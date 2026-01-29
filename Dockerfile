# Define global args
ARG BOT_HOME="/opt/weatherbot"
ARG BOT_USR="botusr"
ARG PY_VERSION="3.9.9"
ARG ALPINE_VERSION="3.14"
ARG WEBHOOK_LISTEN="0.0.0.0"
ARG OWM_KEY
ARG TELEBOT_KEY
ARG WEBHOOK_HOST
ARG WEBHOOK_PORT

# Stage 1: Setup SSL certificates
FROM python:${PY_VERSION}-alpine${ALPINE_VERSION} AS base
LABEL org.opencontainers.image.authors="Yevhen Skyba <skiba.eugene@gmail.com>"

ARG BOT_HOME
ARG BOT_USR
ARG TELEBOT_KEY
ARG WEBHOOK_HOST
ARG WEBHOOK_PORT

USER root

RUN mkdir -p ${BOT_HOME} \
    && addgroup -S ${BOT_USR} \
    && adduser -S ${BOT_USR} -G ${BOT_USR}

RUN apk add --no-cache curl openssl

WORKDIR ${BOT_HOME}

RUN openssl req -newkey rsa:2048 -sha256 -nodes \
    -keyout ${BOT_HOME}/url_private.key \
    -x509 -days 3650 \
    -out ${BOT_HOME}/url_certificate.pem \
    -subj "/C=US/ST=State/O=Organization/CN=${WEBHOOK_HOST}" \
    && curl -s -F "url=https://${WEBHOOK_HOST}:${WEBHOOK_PORT}" \
    -F "certificate=@url_certificate.pem" \
    https://api.telegram.org/bot${TELEBOT_KEY}/setWebhook

# Stage 2: Build application
FROM base
LABEL org.opencontainers.image.authors="Yevhen Skyba <skiba.eugene@gmail.com>"

ARG BOT_HOME
ARG BOT_USR
ARG WEBHOOK_LISTEN
ARG OWM_KEY
ARG TELEBOT_KEY
ARG WEBHOOK_PORT

ENV OWM_KEY=${OWM_KEY}
ENV TELEBOT_KEY=${TELEBOT_KEY}
ENV WEBHOOK_PORT=${WEBHOOK_PORT}
ENV WEBHOOK_LISTEN=${WEBHOOK_LISTEN}

USER root
WORKDIR ${BOT_HOME}

COPY --from=base ${BOT_HOME} ${BOT_HOME}

# Copy requirements and source code
COPY requirements.txt ${BOT_HOME}/
COPY src/ ${BOT_HOME}/src/

RUN apk add --no-cache geos \
    && pip install --no-cache-dir -r requirements.txt \
    && chown -R ${BOT_USR}:${BOT_USR} ${BOT_HOME} \
    && rm -rf /root/.cache

USER ${BOT_USR}

EXPOSE ${WEBHOOK_PORT}

ENTRYPOINT ["python"]
CMD ["src/bot.py"]
