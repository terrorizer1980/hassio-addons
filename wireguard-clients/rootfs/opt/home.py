import os
from flask import Flask, request, render_template, redirect, url_for
import subprocess
from configparser import ConfigParser
#from datetime import datetime, date, time, timedelta
from datetime import datetime, timedelta
import time 
import logging

conf_location = "/etc/wireguard"
app = Flask("Wireguard Clients")
app.config['TEMPLATES_AUTO_RELOAD'] = True

conf_data = {}

# Checked wg show
def get_interfaces():
    conf = []
    for i in os.listdir(conf_location):
        if not i.startswith('.'):
            if ".conf" in i:
                i = i.replace('.conf', '')
                temp = {"conf": i}
                conf.append(temp)
    return conf

def get_configuration_data(config_name):
    # This is required because of postup/postdown etc
    # It has the potential to fail in "correct" .conf files
    # but since we control the format of the .conf file, we can use it
    # DNS, AllowedIPs, Address are transformed to a single line
    config = ConfigParser(allow_no_value=False,strict=False)
    additional = ConfigParser(allow_no_value=False)
    try:
        config.read(conf_location + "/" + config_name + ".conf")

    except Exception:
        return {"confstatus":"invalid"}

    conf_data = {
        "name": config_name,
        "address": config['Interface']['Address'],
        "dns": "",
        "interface_description":"",
        "interface_disabled":"",
        "peer_description":"",
        "confstatus":"valid"
    }
    if config.has_option('Interface', 'DNS'):
        conf_data.update({"dns":config['Interface']['DNS']})

    try:
        additional.read(conf_location + "/" + config_name + ".comments")
    except Exception:
        return conf_data

    if additional.has_option('Interface','Description'):
        conf_data.update({"interface_description":additional['Interface']['Description']})

    if additional.has_option('Interface','Disabled'):
        conf_data.update({"interface_disabled":additional['Interface']['Disabled']})

    if additional.has_option('Peer','Description'):
        conf_data.update({"peer_description":additional['Peer']['Description']})

    return conf_data

# Checked - wg show
def get_running_data(config_name):
    try:
        out = subprocess.check_output(["wg", "show", config_name, "dump"], text=True)
        result = out.splitlines()
        # app.logger.warning(result)

    except Exception:
        return {"status":"stopped"}
        app.logger.warning(Exception)

    # Expected output from this command is : 
    # public-key | private-key | listen-port | fwmark | peers | preshared-keys | endpoints 
    # | allowed-ips | latest-handshakes | transfer-up | transfer-down | persistent-keepalive
    
    entries = result[0].split() + result[1].split()
    conf_data = {
        "listen_port" : entries[2],
        "preshared_key" : entries[5],
        "endpoints" : entries[6],
        "allowed_ips" : entries[7],
        "persistent_keepalive" : entries[11],
        "upload":"",
        "download":"",
        "transfer":"",
        "handshake":"",
        "connected":"",
        "status" : "running"
    }
    
    latest_handshake = entries[8]
    upload = entries[9]
    download = entries[10]

    transfer_total = 0
    download_total = 0
    upload_total = 0

    upload_total = round( ( ( int(upload) / 1024 ) / 1024 ), 4 )
    download_total = round( ( ( int(download) / 1024 ) / 1024 ), 4 )
    transfer_total = round( ( ( ( int(upload) + int(download) ) / 1024 ) / 1024 ), 4 )

    if int(latest_handshake) == 0:
        handshake = "never"
        connected = "no"
    else:
        now = datetime.now()
        minus = now - datetime.fromtimestamp(int(latest_handshake))
        handshake =  str(minus).split(".")[0]
        connected = "yes"

    conf_data.update({"upload":upload_total, "download":download_total, "transfer":transfer_total, "handshake":handshake, "connected":connected})

    return conf_data

@app.route('/', methods=['GET'])
def home():
    x_ingress=""

    if request.headers.get("X-Ingress-Path"):
        x_ingress=request.headers.get("X-Ingress-Path")

    return render_template('home.html', x_ingress=x_ingress)

@app.route('/get_info/', methods=['GET'])
def get_info():
    x_ingress=""

    if request.headers.get("X-Ingress-Path"):
        x_ingress=request.headers.get("X-Ingress-Path")


    alldata=[]

    for i in get_interfaces():

        running=get_running_data(i['conf'])
        configured=get_configuration_data(i['conf'])

        if running["status"] == "stopped" or configured["confstatus"] == "invalid":
            conf_data = {
                "name": i['conf'],
                "interface_description": configured['interface_description'],
                "status": "stopped"
            }
        else: 
            conf_data = {**running, **configured}

        alldata.append(conf_data)

    return render_template('home_in.html', alldata=alldata, x_ingress=x_ingress)


@app.route('/start_stop/<interface>', methods=['GET'])
def start_stop(interface):

    running=get_running_data(interface)
    if request.headers.get("X-Ingress-Path"):
        x_ingress=request.headers.get("X-Ingress-Path")
    else:
        x_ingress='/'

    if running["status"] == "stopped":
        try:
            result = subprocess.check_output(["wg-quick", "up", interface], text=True)

        except Exception:
            return redirect(x_ingress)
            app.logger.warning(Exception)

    else:
        try:
            result = subprocess.check_output(["wg-quick", "down", interface], text=True)

        except Exception:
            return redirect(x_ingress)
            app.logger.warning(Exception)

    time.sleep(1)
    return redirect(x_ingress)

if __name__ == "__main__":

    logging.basicConfig(filename='error.log',level=logging.DEBUG)
    app.run(host='0.0.0.0', debug=False, port=8243)


