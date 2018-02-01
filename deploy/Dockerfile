FROM ubuntu:latest

RUN apt-get update && apt-get install -yq python3 python3-pip vim curl gettext
RUN mkdir /root/aic_site
COPY requirements /root/aic_site/requirements
WORKDIR /root/aic_site/requirements
RUN pip3 install --upgrade pip
RUN pip3 install -r production.txt
COPY . /root/aic_site
