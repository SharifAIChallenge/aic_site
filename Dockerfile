FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -yq python3 python3-pip vim curl
COPY . /root/aic_site
WORKDIR /root/aic_site/config
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.pip

#ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:9000", "aic_site.wsgi"]