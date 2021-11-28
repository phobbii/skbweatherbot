FROM python:3.7.3
LABEL org.opencontainers.image.authors="Eugene Skiba <skiba.eugene@gmail.com>"

ENV BOT_HOME /opt/weatherbot
ENV OWN_KEY "OWN_KEY"
ENV TELEBOT_KEY "TELEBOT_KEY"
ENV WEBHOOK_HOST "YOUR PUBLIC IP"
ENV WEBHOOK_PORT "YOUR HTTPS PORT"
ENV WEBHOOK_LISTEN 0.0.0.0
WORKDIR $BOT_HOME

RUN mkdir -p $BOT_HOME \
    && pip install --upgrade pip \
    && pip install pytelegrambotapi==4.2.0 \
    && pip install pyowm==2.10.0 \
    && pip install datetime==4.3 \
    && pip install pytz==2021.3 \
    && pip install timezonefinder==5.2.0 \
    && pip install aiohttp==3.8.1 \
    && openssl req -newkey rsa:2048 -sha256 -nodes -keyout $BOT_HOME/url_private.key -x509 -days 3560 -out $BOT_HOME/url_certificate.pem -subj "/C=AU/ST=Some-State/O=Internet Widgits Pty Ltd/CN=$WEBHOOK_HOST"\
    && curl -s -F "url=https://$WEBHOOK_HOST:$WEBHOOK_PORT" -F "certificate=@url_certificate.pem" https://api.telegram.org/bot$TELEBOT_KEY/setWebhook

COPY skbweatherbot.py $BOT_HOME

EXPOSE $WEBHOOK_PORT
CMD [ "python", "./skbweatherbot.py" ]
