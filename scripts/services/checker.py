#!/bin/python3

import subprocess
import sys
sys.path.append('/opt/terminator/')
import re
from terminator import UsbHubInitiator
from utils.mysql_utils import TerminatorDB
import os
import time
import datetime


main_iface = os.getenv('INPUT_IFACE', 'enp0s25')
os.environ["PATH"] = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin" 
scripts_path = "/opt/terminator/scripts"
log_file = "/var/log/terminator.log"

def write_log(msg):
    now = datetime.datetime.today().strftime('%d-%m-%y %H:%M:%S')
    with open(log_file, "a") as f:
        f.write(f'[checker][{now}]\t\t{msg}\n')

def ifconfig():
    ifconfig_lines = subprocess.run(["ifconfig"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().split('\n')
    return ifconfig_lines

def get_ifaces_and_ip():
    ethernet_pattern = re.compile("^e.*: .*$")
    ifconfig_lines = ifconfig()
    iface_ip = []
    for i, l in enumerate(ifconfig_lines):
        if ethernet_pattern.match(l) and main_iface not in l:
            iface = l.split(':')[0]
            try:
                ip = ifconfig_lines[i + 1].split(' ')[9]
            except:
                ip = None
            iface_ip.append((iface, ip))
    return iface_ip

def fix_missing_interface():
    for interface, ip in get_ifaces_and_ip():
        initiator = UsbHubInitiator(interface)
        wanted_ip = initiator.get_iface_usb_port()[-1]
        if ip != wanted_ip:
            write_log(f"missing interface found [{interface}]")
            initiator.handle_event("add")

def check_already_processing(iface):
    ps = subprocess.run(
            [f"ps aux | grep /bin/python3 /opt/terminator/terminator | grep -v grep"],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE).stdout.decode().strip('\n')
    ps_ = subprocess.run(
            [f"ps aux | grep /opt/terminator/scripts/proxy_manager.py | grep {iface} | grep -v grep"],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE).stdout.decode().strip('\n')
    return bool(ps or ps_)

def health_check():
    current_ips = [x[1] for x in get_ifaces_and_ip()]
    db = TerminatorDB("terminator", "n5cHK9pBt1oAdcY!!")
    ip_pattern = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    all_ports = db.get_all_ports()
    write_log("Checking terminator health")
    for port in all_ports:
        usb_port = port[0]
        interface = port[1]
        if check_already_processing(interface):
            continue
        ip = port[2]
        if ip not in current_ips:
            db.update_interface_infos(usb_port, '', '', 'empty')
            continue
        write_log(f"testing internet for interface [{interface}] on port [{usb_port}]")
        curl = subprocess.run([f"curl --interface {interface} eth0.me --connect-timeout 15"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip('\n')
        is_up = bool(ip_pattern.match(curl))
        if is_up:
            db.update_interface_infos(usb_port, interface, ip, 'up', public_ip=curl)
            write_log(f"Proxy {ip} is up")
        else:
            db.update_interface_infos(usb_port, interface, ip, 'down')
            write_log(f"Proxy {ip} is down")

if __name__ == "__main__":
    write_log("checking missing interfaces")
    fix_missing_interface()
    time.sleep(3)
    write_log("testing internet for ports")
    health_check()





