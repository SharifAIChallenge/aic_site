FROM ubuntu:latest

RUN apt-get update && apt-get install -yq python3 python3-pip vim curl gettext
COPY . /root/aic_site
WORKDIR /root/aic_site/requirements
RUN pip3 install --upgrade pip
RUN pip3 install -r production.txt