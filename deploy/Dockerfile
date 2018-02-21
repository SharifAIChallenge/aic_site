FROM python:latest

RUN apt-get update && apt-get install -yq vim curl gettext
#RUN apt-get update && apt-get install -yq python3.5 python3-pip vim curl gettext
#RUN apt-get update && apt-get install software-properties-common -y && add-apt-repository ppa:jonathonf/python-3.6 -y && apt-get update && apt-get install python3.6 python3-dev python3-pip vim curl gettext -y && rm /usr/bin/python3 && ln -s /usr/bin/python3.6 /usr/bin/python3
RUN mkdir /root/aic_site
COPY requirements /root/aic_site/requirements
WORKDIR /root/aic_site/requirements
RUN pip3 install --upgrade pip
RUN pip3 install -r production.txt
COPY . /root/aic_site
