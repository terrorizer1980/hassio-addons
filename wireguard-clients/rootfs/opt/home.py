import os
from flask import Flask, request, render_template, redirect, url_for
import subprocess
from configparser import ConfigParser
from datetime import datetime, date, time, timedelta

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

    if additional.has_option('Peer','Description'):
        conf_data.update({"peer_description":additional['Peer']['Description']})

    return conf_data

# Checked - wg show
def get_running_data(config_name):
    try:
    	result = subprocess.run(["wg", "show", config_name, "dump"], stdout=subprocess.PIPE)
    	tmpres = result.stdout.splitlines()

    except Exception:
        return {"status":"stopped"}

    if result.returncode > 0:
        return {"status":"stopped"}

    part0 = tmpres[0].decode("UTF-8").split()
    part1 = tmpres[1].decode("UTF-8").split()

    # private_key = part0[0]
    # public_key = part0[1]
    # fwmark = part0[3]
    # peer_public_key = part1[0]
    #
    conf_data = {
        "listen_port" : part0[2],
        "preshared_key" : part1[1],
        "endpoints" : part1[2],
        "allowed_ips" : part1[3],
        "persistent_keepalive" : part1[7],
        "upload":"",
        "download":"",
        "transfer":"",
        "handshake":"",
        "status" : "running"
    }
    
    upload = part1[5]
    download = part1[6]
    latest_handshake = part1[4]

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

    alldata=[]

    for i in get_interfaces():

        running=get_running_data(i['conf'])
        configured=get_configuration_data(i['conf'])

        if running["status"] == "stopped" or configured["confstatus"] == "invalid":
            conf_data = {
                "name": i['conf'],
                "status": "stopped"
            }
        else: 
            conf_data = {**running, **configured}

        alldata.append(conf_data)

    return render_template('home_in.html', alldata=alldata)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=8243)


