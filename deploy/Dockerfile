FROM ubuntu:latest

RUN apt-get update && apt-get install -yq software-properties-common python-software-properties && add-apt-repository ppa:jonathonf/python-3.6 -y && apt-get update && apt-get install -yq python3.6 python3-pip gettext
RUN mkdir /root/aic_site
COPY requirements /root/aic_site/requirements
WORKDIR /root/aic_site/requirements
RUN pip3 install --upgrade pip
RUN pip3 install -r production.txt
COPY . /root/aic_site
