FROM python:3.8-slim AS bot

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

# Env vars
ENV TELEGRAM_TOKEN ${TELEGRAM_TOKEN}

RUN apt-get update
RUN apt-get install -y python3 python3-pip python-dev build-essential python3-venv

#RUN mkdir -p /codebase /storage
#ADD . /codebase
#WORKDIR /codebase

#RUN pip3 install -r requirements.txt
#RUN chmod +x /codebase/bot.py

#CMD python3 /codebase/bot.py;

#Use bash on docker
SHELL [ "/bin/bash" , "-c" ]

#Use bash on ubuntu 
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Reconfigure locale
#RUN locale-gen en_US.UTF-8 && dpkg-reconfigure locales

#Root password is now Docker! -> go into root using "su"
RUN echo 'root:Docker!' | chpasswd

ENV USER_NAME mm
ARG host_uid=1001
ARG host_gid=1001

RUN groupadd -g $host_gid $USER_NAME && useradd -g $host_gid -m -s /bin/bash -u $host_uid $USER_NAME
RUN echo "$USER_NAME:$USER_NAME" | chpasswd && adduser $USER_NAME sudo
USER $USER_NAME

#pip install telegram
#pip install python-telegram-bot==13.7
#pip install htmldom

