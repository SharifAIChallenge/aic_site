FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -yq python3 python3-pip vim curl
RUN pip3 install Django==1.11 gunicorn
COPY . /root/aic_site
WORKDIR /root/aic_site

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:9000", "aic_site.wsgi"]