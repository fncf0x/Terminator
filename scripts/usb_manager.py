#!/bin/python3
import subprocess
import sys


def get_nuc_and_sim(sim):
    sim_virtual_number = int(sim.replace('sim', ''))
    nuc_number = int(sim_virtual_number > 16) + 1
    sim_physical_number = sim_virtual_number % 16
    sim_physical_number = sim_physical_number if sim_physical_number else 16
    return (nuc_number, sim_physical_number)

def get_nuc_tty(nuc_number):
    find_tty = subprocess.run(
            [f'grep -r "tty" /sys/bus/usb/devices/usb3/3-{nuc_number}/'],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE).stdout.decode()
    tty_path = find_tty.split("=")[-1].rstrip()
    return tty_path

def hard_reset_port(tty, port):
    cmd = f'/opt/terminator/bin/cusbi /S:{tty} 0:{port}'
    subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode()
    cmd = f'/opt/terminator/bin/cusbi /S:{tty} 1:{port}'
    subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage:  {sys.argv[0]} <SOFT|HARD> <SIM_NUMBER>')
        exit(1)
    virtual_sim = sys.argv[2]
    mode = sys.argv[1]
    nuc, sim = get_nuc_and_sim(virtual_sim)
    if mode.lower() == "hard":
        tty_port = get_nuc_tty(nuc)
        if tty_port:
            hard_reset_port(tty_port, sim)
    if mode.lower() == "soft":
        print("soft_reset")  # not implemented yet
        pass
    exit(0)
