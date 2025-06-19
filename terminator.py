#!/bin/python3

import os
import json
import subprocess
import re
import time
import sys
import datetime
from threading import Thread
from utils.mysql_utils import TerminatorDB
from random import uniform


class UsbHubInitiator:

    def __init__(self, iface):

        self.proxies = TerminatorDB('terminator', 'n5cHK9pBt1oAdcY!!')

        os.environ['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin'
        self.input_interface = os.getenv("INPUT_IFACE", self.get_main_iface())
        self.ip_prefix = os.getenv("IP_PREFIX", "192.168.8")
        self.proxy_port = os.getenv('PROXY_PORT', '1337')
        
        self.log_file = "/var/log/terminator.log"
        self.scripts_path = "/opt/terminator/scripts"

        self.iface = iface

    def write_log(self, log):
        time = datetime.datetime.today().strftime('%d-%m-%y %H:%M:%S')
        with open(self.log_file, "a") as f:
            f.write(f'[terminator][{time}]:\t{log}\n')

    def get_main_iface(self):
        return "enp0s25"
        #return [v for v in subprocess.run(['ifconfig'], stdout=subprocess.PIPE).stdout.decode().split('\n') if 'enp' in v][0].split(':')[0]

    def get_iface_usb_port(self):
        iface = self.iface
        port_pattern = re.compile(".*devices\/.-.\..\..\/.*")
        out = subprocess.run([f'grep -r "INTERFACE={iface}" /sys/bus/usb/devices/*'], stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE).stdout.decode()
        raw_port = [l for l in out.split('\n') if port_pattern.match(l)][0].split('devices/')[1].split('/')[0].split('-')[1]
        nuc_port = raw_port.split('.')[0]
        dongle_port = str((int(raw_port.split('.')[1]) - 1) * 4 + int(raw_port.split('.')[2])).zfill(2)
        ip = f"{self.ip_prefix}.{nuc_port}{dongle_port}"
        return (nuc_port, dongle_port, ip)
 
    def set_static_ip(self, ip):
        gw_ip = f"{'.'.join(ip.split('.')[:3])}.1"
        iface = self.iface
        self.write_log(f"[Configuring IP] {iface}")
        subprocess.run([f"ifconfig {iface} {ip} netmask 255.255.255.0"], shell=True, stdout=subprocess.PIPE)
        subprocess.run([f"route del -net default netmask 0.0.0.0 metric 0 dev {iface}"], shell=True, stdout=subprocess.PIPE)
        subprocess.run([f"route add default gw {gw_ip} {iface}"], shell=True, stdout=subprocess.PIPE)
        self.write_log(f"[Configuring IP] binded IP {ip} to interface {iface}")

    def start_proxy(self):
        self.write_log(f"[Starting proxy] {self.iface}")
        cmd = f"{self.scripts_path}/proxy_manager.py start {self.iface}"
        os.system(cmd)

    def stop_proxy(self):
        self.write_log(f"[Starting proxy] {self.iface}")
        cmd = f"{self.scripts_path}/proxy_manager.py stop {self.iface}"
        os.system(cmd)

    def handle_event(self, event):
        ethernet_pattern = re.compile("^e.*$")
        if self.iface == self.input_interface or not ethernet_pattern.match(self.iface):
            exit(0)
        if event in ["add", 'move']:
            msg = f"[New interface detected] {self.iface}"
            self.write_log(msg)
            time.sleep(2)
            nuc_port, dongle_port, ip = self.get_iface_usb_port()
            self.set_static_ip(ip)
            msg = f"[Interface added] NAME->{self.iface} PORT->[{nuc_port}:{dongle_port}] IP->{ip}"
            self.write_log(msg)
            self.proxies.update_interface_infos(f'{nuc_port}_{dongle_port}', self.iface, ip, "plugged")
            self.start_proxy()
            subprocess.run([f"dhclient {self.iface}"], shell=True, stdout=subprocess.PIPE)
        elif event == "remove":
            ip = [p[2] for p in self.proxies.get_all_ports() if p[1] == self.iface][0]
            self.write_log(ip)
            msg = f"[Interface removed] {self.iface}"
            self.stop_proxy()
            subprocess.run([f"route del -net default netmask 0.0.0.0 dev {self.iface}"], shell=True, stdout=subprocess.PIPE)
            subprocess.run(["dhclient"], shell=True, stdout=subprocess.PIPE)
            self.write_log(msg)
            time.sleep(3)
            self.proxies.clean_port(self.iface)


if __name__ == "__main__":
    t = datetime.datetime.today().strftime('%d-%m-%y %H:%M:%S')
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} IFACE EVENT")
        exit(1)
    os.chdir('/opt/terminator')
    interface = sys.argv[1]
    event = sys.argv[2]
    Initiator = UsbHubInitiator(interface)
    Initiator.handle_event(event)
    exit(0)

