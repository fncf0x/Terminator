#!/bin/python3

import os
import sys
sys.path.append("/opt/terminator")
from utils.mysql_utils import TerminatorDB
from flask import Flask, jsonify, request


app = Flask(__name__)
db = TerminatorDB('terminator', 'n5cHK9pBt1oAdcY!!')
API_KEY = "supersecret"
TERMINATOR_PATH = "/opt/terminator"


def check_auth(request):
    if not request.args.get("api_key"):
        return "Missing API key"
    if request.args.get("api_key") != API_KEY:
        return "forbidden"

@app.route("/list_proxies", methods=["GET"])
def list_proxies():
    if msg:= check_auth(request):
        return jsonify(msg)
    ports = []
    if request.method=='GET':
        for port in db.get_all_ports():
            ports.append({
                "port_position": port[0],
                "local_ip": port[1],
                "public_ip": port[2],
                "status": port[3],
            })

        return jsonify(ports)

@app.route("/reboot", methods=["GET"])
def reboot():
    if msg:= check_auth(request):
        return jsonify(msg)
    if request.method=='GET':
        os.system(f"{TERMINATOR_PATH}/monitoring/reset_files")
        os.system("reboot")
        return jsonify("rebooting device")

@app.route("/reset_port", methods=["GET"])
def reset_port ():
    if msg:= check_auth(request):
        return jsonify(msg)
    if request.method=='GET':
        port = request.args.get("port")
        if not port:
            return jsonify("missing port number")
        os.system(f"{TERMINATOR_PATH}/scripts/usb_manager.py hard {port}")
        return jsonify("port is being reset")

