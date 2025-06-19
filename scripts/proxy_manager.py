#!/bin/python3

import sys
import time
sys.path.append('/opt/terminator/')
from terminator import UsbHubInitiator
from utils.mysql_utils import TerminatorDB
import subprocess
import os
import datetime


log_file = "/var/log/terminator.log"
db_path = "/opt/terminator/db/terminator.db"

def write_log(msg):
    now = datetime.datetime.today().strftime('%d-%m-%y %H:%M:%S')
    with open(log_file, "a") as f:
        f.write(f'[proxy manager][{now}]\t{msg}\n')

def start_proxy(interface, ip):
    write_log(f"starting proxy {interface} {ip}")
    cmd = f"proxy -d -i{ip} -Di{interface} -De{interface} -p1337"
    os.system(cmd)


def stop_proxy(interface, ip):
    write_log(f"stopping proxy {interface} {ip}")
    cmd = f"netstat -anptl | grep -Ei '{ip}:1337'"
    netstat = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip(" ").split('\n')
    for line in netstat:
        try:
            pid = line.split("/proxy")[0].split(' ')[-1]
        except:
            pid = None
        if pid:
            cmd = f"kill -9 {pid}"
            write_log(f"killing {cmd} {interface} {ip}")
            subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {sys.argv[0]} start|stop interface")
        exit(1)
    os.chdir('/opt/terminator')
    mode = sys.argv[1]
    interface = sys.argv[2]

    if mode == "start":
        initiator = UsbHubInitiator(interface)
        ip = initiator.get_iface_usb_port()[-1]
        stop_proxy(interface, ip)
        time.sleep(1)
        start_proxy(interface, ip)
        exit(0)
    if mode == "stop":
        db = TerminatorDB("terminator", "n5cHK9pBt1oAdcY!!")
        ip = db.get_iface_ip(interface)
        stop_proxy(interface, ip)
        exit(0)
