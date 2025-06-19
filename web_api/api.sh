#!/bin/bash

cd /opt/terminator/web_api/
sleep 10
flask --app api run --port 8080 --host 0.0.0.0

