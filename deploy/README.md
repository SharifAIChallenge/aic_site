# [Sharif AI Challenge site Deployment server](https://aichallenge.sharif.edu/) &middot; [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)] [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]

Sharif AI Challenge 2018 private deployment server.

## deploy_server.py

the main deployment server. a RESTful api written in flask.

```python
#! /usr/bin/python3

import subprocess
import sys

from flask import Flask, send_from_directory, render_template, request, abort
from flask_restful import Api

app = Flask(__name__, static_url_path='')
api = Api(app)

TOKEN = <CONFIDENTIAL>
INITIAL_LOG_COUNTER = 0
SERVER_IP = <CONFIDENTIAL>
PORT = <CONFIDENTIAL>
SERVER_URL = 'http://' + SERVER_IP + ':' + str(PORT)


@app.route('/deploy_test')
def deploy_test():
    global INITIAL_LOG_COUNTER, TOKEN

    if request.headers.get('X-token') is not None and request.headers.get('X-token') == TOKEN:
        print("valid_token!")
        deploy_command = 'cd /home/aicsdep && ./deploy_test.sh > logs/log_{}.txt'.format(INITIAL_LOG_COUNTER)
        INITIAL_LOG_COUNTER += 1
        deploy_process = subprocess.Popen(deploy_command, shell=True, stdout=subprocess.PIPE)
        return str(render_template('response.html', deployment_type='Test Deployment',
                                   log_file='{}/logs/log_{}.txt'.format(SERVER_URL, INITIAL_LOG_COUNTER - 1)))
    else:
        print("invalid_token!")
        return abort(403)


@app.route('/deploy_production')
def deploy_production():
    global INITIAL_LOG_COUNTER, TOKEN

    if request.headers.get('X-token') is not None and request.headers.get('X-token') == TOKEN:
        print("valid_token!")
        deploy_command = 'cd /home/aicsdep && ./deploy.sh > logs/log_{}.txt'.format(INITIAL_LOG_COUNTER)
        INITIAL_LOG_COUNTER += 1
        deploy_process = subprocess.Popen(deploy_command, shell=True, stdout=subprocess.PIPE)
        return str(render_template('response.html', deployment_type='Production Deployment',
                                   log_file='{}/logs/log_{}.txt'.format(SERVER_URL, INITIAL_LOG_COUNTER - 1)))
    else:
        print("invalid_token!")
        return abort(403)


@app.route('/logs/<path:path>')
def send_js(path):
    return send_from_directory('logs', path)


def main():
    app.run(port=PORT, host="0.0.0.0")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])
    try:
        main()
    except Exception as exception:
        print(exception, exception.args)
        main()

```

in order to initiate_deployment to servers one must use this commands

```bash
curl -H "X-token: $(TOKEN)"  -X GET http://$SERVER_URL/deploy_production
curl -H "X-token: $(TOKEN)"  -X GET http://$SERVER_URL/deploy_test
```

script requirements:

```
aniso8601==2.0.0
click==6.7
Flask==0.12.2
Flask-Jsonpify==1.5.0
Flask-RESTful==0.3.6
itsdangerous==0.24
Jinja2==2.10
MarkupSafe==1.0
pytz==2017.3
six==1.11.0
Werkzeug==0.14.1

```

## templates/response.html

html flask template used for rendering server responses:

```djangotemplate
<!DOCTYPE html>
<html>
<head>
    <title>{{ deployment_type }}</title>
</head>
<body>

{% if name %}
<h1>{{ deployment_type }} in progress!</h1>
{% else %}
<p>deployment log will be available on <a href='{{ log_file }}'>{{ log_file }}</a></p>
{% endif %}

</body>
</html>
``` 

## deploy.sh

script used for deployment to production server:

```bash
#!/usr/bin/env bash

mkdir deployment
cd deployment
git clone https://github.com/SharifAIChallenge/aic_site.git
git checkout master
cd aic_site
cp ../../build_scripts/production_secret.py aic_site/settings/
cd deploy
cp ../../../build_scripts/build.sh .
./build.sh

cd ../../..
rm -rf deployment
```

## deploy_test.sh

script used for deployment to production_test server:

```bash
#!/usr/bin/env bash

mkdir deployment_test
cd deployment_test
git clone https://github.com/SharifAIChallenge/aic_site.git
git checkout stable-dev
cd aic_site
cp ../../build_scripts/production_secret.py aic_site/settings/
cd deploy
cp ../../../build_scripts/build_test.sh .
./build_test.sh

cd ../../..
rm -rf deployment_test
```

## systemd service_script (deploy_server.service)

```
[Unit]
Description=aic18 site deployment service
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
ExecStart=/path/to/script/folder/deploy_server.py

[Install]
WantedBy=multi-user.target
```

after copying this file to /lib/systemd/system/ one should enter this commands for service to start working:

```
systemctl daemon-reload
systemctl start deploy_server.service
systemctl enable deploy_server.service
``` 

useful commands:

```
systemctl stop deploy_server.service
systemctl status deploy_server.services
```

