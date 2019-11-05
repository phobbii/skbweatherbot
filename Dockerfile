FROM python:3.7.3
MAINTAINER "Eugene Skiba <skiba.eugene@gmail.com>"

ENV BOT_HOME /opt/weatherbot
ENV OWN_KEY "OWN_KEY"
ENV TELEBOT_KEY "TELEBOT_KEY"
WORKDIR $BOT_HOME

RUN mkdir -p $BOT_HOME \
    && pip install --upgrade pip \
    && pip install pytelegrambotapi \
    && pip install pyowm \
    && pip install datetime \
    && pip install pytz \
    && pip install timezonefinder

COPY skbweatherbot.py $BOT_HOME

CMD [ "python", "./skbweatherbot.py" ]