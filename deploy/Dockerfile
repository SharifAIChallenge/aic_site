FROM python:latest

RUN apt-get update && apt-get install -yq vim curl gettext
RUN apt-get install -yq redis-server
RUN mkdir /root/aic_site
COPY requirements /root/aic_site/requirements
WORKDIR /root/aic_site/requirements
RUN pip3 install --upgrade pip
RUN pip3 install -r production.txt
COPY . /root/aic_site
