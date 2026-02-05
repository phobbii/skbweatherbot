# =========================
# Build-time variables for FROM
# =========================
ARG PY_VERSION=3.9.9
ARG ALPINE_VERSION=3.14

FROM python:${PY_VERSION}-alpine${ALPINE_VERSION}

# -------------------------
# Build-time arguments for container
# -------------------------
ARG BOT_HOME=/opt/weatherbot
ARG BOT_USR=botusr
ARG WEBHOOK_HOST

LABEL org.opencontainers.image.authors="Yevhen Skyba <skiba.eugene@gmail.com>"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# -------------------------
# System dependencies + non-root user
# -------------------------
RUN apk add --no-cache geos openssl \
 && addgroup -S ${BOT_USR} \
 && adduser -S ${BOT_USR} -G ${BOT_USR} \
 && mkdir -p ${BOT_HOME}

WORKDIR ${BOT_HOME}

# -------------------------
# Generate SSL certificates
# -------------------------
RUN openssl req -newkey rsa:2048 -sha256 -nodes \
        -keyout url_private.key \
        -x509 -days 3650 \
        -out url_certificate.pem \
        -subj "/C=US/ST=State/O=Organization/CN=${WEBHOOK_HOST}" \
 && apk del openssl

# -------------------------
# Python dependencies
# -------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------
# Application source
# -------------------------
COPY src/ ${BOT_HOME}/
RUN chown -R ${BOT_USR}:${BOT_USR} ${BOT_HOME}

# -------------------------
# Switch to non-root user
# -------------------------
USER ${BOT_USR}

ENTRYPOINT ["python"]
CMD ["bot.py"]
