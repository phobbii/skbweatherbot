# Define global args
ARG BOT_HOME="/opt/weatherbot/"
ARG BOT_USR="botusr"
ARG PY_VERSION="3.9.9"
ARG ALPINE_VERSION="3.14"
ARG WEBHOOK_LISTEN="0.0.0.0"
ARG OWN_KEY
ARG TELEBOT_KEY
ARG WEBHOOK_HOST
ARG WEBHOOK_PORT

# Stage 1
FROM python:${PY_VERSION}-alpine${ALPINE_VERSION} AS base
LABEL org.opencontainers.image.authors="Yevhen Skyba <skiba.eugene@gmail.com>"

# Include global args in this stage of the build
ARG BOT_HOME="/opt/weatherbot/"
ARG BOT_USR="botusr"
ARG TELEBOT_KEY
ARG WEBHOOK_HOST
ARG WEBHOOK_PORT

# Set root
USER root

# Create bot home and user
RUN mkdir -p ${BOT_HOME} \
    && addgroup -S ${BOT_USR} \
    && adduser -S ${BOT_USR} -G ${BOT_USR}

# Install openssl dependencies
RUN apk add --no-cache \
    curl \
    openssl

# Set working directory to bot home
WORKDIR ${BOT_HOME}

# Generate self-signed certificate
RUN openssl req -newkey rsa:2048 -sha256 -nodes -keyout ${BOT_HOME}/url_private.key -x509 -days 3560 -out ${BOT_HOME}/url_certificate.pem -subj "/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=${WEBHOOK_HOST}"\
    && curl -s -F "url=https://${WEBHOOK_HOST}:${WEBHOOK_PORT}" -F "certificate=@url_certificate.pem" https://api.telegram.org/bot${TELEBOT_KEY}/setWebhook

# Stage 2
FROM base
LABEL org.opencontainers.image.authors="Yevhen Skyba <skiba.eugene@gmail.com>"

# Include global args in this stage of the build
ARG BOT_HOME="/opt/weatherbot/"
ARG BOT_USR="botusr"
ARG WEBHOOK_LISTEN="0.0.0.0"
ARG OWN_KEY
ARG TELEBOT_KEY
ARG WEBHOOK_PORT

# Define environment variables
ENV OWN_KEY ${OWN_KEY}
ENV TELEBOT_KEY ${TELEBOT_KEY}
ENV WEBHOOK_PORT ${WEBHOOK_PORT}
ENV WEBHOOK_LISTEN ${WEBHOOK_LISTEN}

# Set root
USER root

# Set working directory to bot home
WORKDIR ${BOT_HOME}

# Copy dependencies
COPY --from=base ${BOT_HOME} ${BOT_HOME}

# Copy required files
COPY requirements.txt skbweatherbot.py ${BOT_HOME}

# Install bot dependencies
RUN apk add --no-cache geos \
    && chown -R ${BOT_USR}. ${BOT_HOME} \
    && pip install --no-use-pep517 -r requirements.txt \
    && rm -rf requirements.txt

# Set service user
USER ${BOT_USR}

EXPOSE ${WEBHOOK_PORT}
ENTRYPOINT [ "python" ]
CMD [ "./skbweatherbot.py" ]