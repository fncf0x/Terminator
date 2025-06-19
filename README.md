# 4G USB PROXY #
![Arch](docs/Arch.png)


### What is this project ? ###

Introducing 4G USB PROXY: a complete setup of hardware and software designed to create a stable mobile proxy. With the ability to change IP addresses and automatically configure USB dongles, this system allows users to easily obtain IPs from specific countries using only SIM cards.


## Setup ##
### Requirement ###
#### Hardware ####
* 1 or 2 [NUC](https://www.amazon.fr/Fujitsu-Esprimo-Q0920P0048DE-Ordinateur-certifi%C3%A9/dp/B0854LM164/ref=sr_1_16?__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=3515D2DZX3OBS&dib=eyJ2IjoiMSJ9.bO5BCdPrYUglkv5sWH1py3CbipXAD3CDrTf2aqBnvhnpDQnO2ds_6BdGZ7NXslyvXOxYckbqJngtZUpe48TJB3jXiO-9vZplo9zOlyHNt_g57mZuRk2SdcgUl846SZWoGfl-5BfeY1tYGH4AGVrgH9XWJ5PmLYl150zsaF1imS1Xw3k3frbnVd8gU_ppFB6fY0TLf46Iff5yzWsGFr0wpbOYthATUxAEHVjmD92736PSxL3fcWynnhzrKzldpZK5gcMF8uySA4UT9Azjld1VM_5o74deWcSso-jlozq5ZMw.pdG7c8RmOmkgV0JUOzNqV_gI9A64TfrA2vpxC24UdXc&dib_tag=se&keywords=NUC&qid=1715610948&s=computers&sprefix=nuc%2Ccomputers%2C64&sr=1-16) or any mini station (scalable i,e 1 NUC = 32 PORT).
* 2 USB HUB per NUC ([ExSys](https://www.amazon.fr/EXSYS-EX-1116HMVS/dp/B00GTS6M1I/ref=sr_1_1?__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&dib=eyJ2IjoiMSJ9.XyKSDOBdgWmIOFwfYjN-NF3QbUQvgENtyuDywYCfDJt3p10DRu69j3YWA_YFOIwrTpStPYAQ_iOGlgP2NTI9VU3TnsRnJLHiCrXLCUbdQE9B4cNL7GB12HzVtldHPdHMi61esktLTeJ9w-6gTLRh_jSjYUgtHVsQ05bH-ZhfJ7DCZc5MdXjnRHDMnnNVcHYRdQq1635fA2tGleceKDkRSbfDyp-usOkBwzU48s6wUoZURec6u3WRYZkwH9LdctHZTgFwsJkAjKIpxeOvJk4vbxJaWwkuditxlhx2Y3VJjgQ.SMr4lDE3dEOuN_nu1wOjtKYTzNPfgUKcWDHeN9jQi4s&dib_tag=se&keywords=exsys+16+ports&qid=1715610836&s=computers&sr=1-1) or any managable USB HUB).
* 1 Main server to group the NUCs, any station is good (>=16GB RAM, Intel >= i5)
* 1 screen for on site monitoring.
* USB 4G Dongles (32 per NUC).
* 32 SIM cards per NUC.
* GSM repeater if the signal is not good (RSSI -32 is the best).
#### Software ####
#### Nuc: ####
* OS: Ubuntu >= 22.04.1 LTS x86_64.
* Python >= 3.10.12 with the [requirement](requirements.txt).
* HAProxy 2.4.22.
* 3proxy-0.9.3.
#### Main Server: ####
* OS: Ubuntu >= 22.04.1 LTS x86_64
* HAProxy 2.4.22.
* Python >= 3.10.12 with the [requirement](requirements.txt).



## NUC Setup
### Installation Steps
1. **Install Ubuntu:**
   - Download Ubuntu from the [official website](https://ubuntu.com/download/server) and create a bootable USB drive.
   - Boot your system from the USB drive and follow the installation wizard to install Ubuntu.

2. **Python Installation:**
   - Check Python version:
     ```bash
     python --version
     ```
   - If Python is not installed or is an older version, install Python:
     ```bash
     sudo apt update
     sudo apt install python3
     ```

3. **HAProxy Installation:**
   - Update package index:
     ```bash
     sudo apt update
     ```
   - Install HAProxy:
     ```bash
     sudo apt install haproxy
     ```

4. **3proxy Installation:**
   - Download 3proxy from the [official website](https://github.com/z3APA3A/3proxy/releases) and extract it.
   - Install 3proxy:
     ```bash
     cd <path_to_3proxy_directory>
     make -f Makefile.Linux
     sudo make -f Makefile.Linux install
     ```

5. **Clone Repository and Setup:**
   - Clone the repository:
     ```bash
     git clone https://bitbucket.org/dataimpact/4g_usb_proxy /opt/terminator/
     mv /opt/test /opt/terminator
     ```
   - Navigate to the "terminator" directory:
     ```bash
     cd /opt/terminator
     ```
   - Add the provided crontab:
     ```bash
     # Add crontab command here
     ```
   - Copy `90-netifchanges.rules` from the "udev_rules" directory to the udev rules directory:
     ```bash
     cp udev_rules/90-netifchanges.rules /etc/udev/rules.d/
     ```
   - Copy `api.service` and `checker.service` from the "scripts/services" directory to the services directory, enable them, and start them:
     ```bash
     cp scripts/services/api.service scripts/services/checker.service /etc/systemd/system/
     systemctl enable api.service
     systemctl enable checker.service
     systemctl start api.service
     systemctl start checker.service
     ```
   - Copy the contents of `haproxy/NUC/*` to `/etc/haproxy/`:
     ```bash
     cp haproxy/NUC/* /etc/haproxy/
     ```
   - Plug in USB hubs and reboot:
     ```bash
     reboot
     ```
   - Plug in the screen.
   - Monitor dongles:
     ```bash
     cd /opt/terminator/monitoring
     ./logs
     ```

## Main Server Setup
### Installation Steps
1. **Repeat Steps 1-4 from NUC Setup.**

2. **Clone Repository and Setup:**
   - Clone the repository:
     ```bash
     git clone http://github.com/test /opt/terminator/
     mv /opt/test /opt/terminator
     ```
   - Navigate to the "terminator" directory:
     ```bash
     cd /opt/terminator
     ```
   -  Copy the contents of `haproxy/SERVER/*` to `/etc/haproxy/`:
       ```bash
       cp haproxy/SERVER/* /etc/haproxy/
       ```
   - Reboot the main server:
       ```bash
       reboot
       ```

# How to Use #

## Using SIM Cards ##
To use a SIM card, you can use the following commands:
- Using SIM1:
```bash
curl -x http://sim1:test@main_server_ip:5000 ipinfo.io/json
```
- Using SIM4:
```bash
curl -x http://sim4:test@main_server_ip:5000 ipinfo.io/json
```
## Listing Available Proxies ##
To list available proxies, you can use the following command:
```bash
curl main_server_ip:8080/list_proxies?api_key=supersecret | jq .
```

## Resetting a Port ##
To reset a port, you can use the following command:
```bash
curl 'http://main_server_ip:8080/reset_port?port=sim4&api_key=supersecret'
```

## Rebooting Everything ##
To reboot everything, you can use the following command:
```bash
curl 'http://10.101.20.50:8080/reboot?api_key=supersecret'
```

Replace main_server_ip with the IP address of your main server. Ensure to replace supersecret with your actual API key for authentication purposes.

