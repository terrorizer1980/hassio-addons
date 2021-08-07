# Home Assistant Add-on: WireGuard Clients

[WireGuard®][wireguard] is an extremely simple yet fast and modern VPN that
utilizes state-of-the-art cryptography. It aims to be faster, simpler, leaner,
and more useful than IPsec, while avoiding the massive headache.

It intends to be considerably more performant than OpenVPN. WireGuard is
designed as a general-purpose VPN for running on embedded interfaces and
supercomputers alike, fit for many different circumstances.

Initially released for the Linux kernel, it is now cross-platform (Windows,
macOS, BSD, iOS, Android) and widely deployable,
including via an Hass.io add-on!

WireGuard is currently under heavy development, but already it might be
regarded as the most secure, easiest to use, and the simplest VPN solution
in the industry.

## Authors & contributors

Project started as fork from Fabio Mauro's
https://github.com/bigmoby/addon-wireguard-client
which was a fork of Franck Nijhof's
https://github.com/hassio-addons/addon-wireguard

Both are under MIT license
Parts Copyright (c) 2020-2021 Fabio Mauro
Parts Copyright (c) 2019-2020 Franck Nijhof

Frontend inspired by Donald Zhou's
https://github.com/donaldzou/wireguard-dashboard
Available under Apache License v2
Parts Copyright (c) 2021 Donald Zou

## Installation

You are reading this, so you obviously already know where 
to find this addon. Just install in Home Assistant as an Addon. 
You can create as many Wireguard tunnels as you want. The keys
(private, public and preshared if you wish to use one) should be 
generated in another system - the server looks like a good option.

## Security considerations

Be aware that the container is based on python enabled images of alpine
ghcr.io/hassio-addons/base-python/

These images have IPv4 forwarding enabled. They also have iptables installed.
WireGuard (and subsequently this addon) allows you to add commands to be executed 
before / after the interface is coming up or down. 

In plain English, if you want to expose your computer to the whole internet
you can actually do so; although acting as a client there is a safety measure.

Still, my suggestion is that if you don't know **exactly** what to do with
PostUp, PreUp, PostDown and PreDown, leave them empty. 

## Configuration

The configuration allows all valid options for a WireGuard Client 
except for MTU and Table; the default settings make perfect sense

Options that are only for the server are not allowed - such as ListenPort

Three options won't be added to the Wireguard configuration, but can be used
and 2 of them shown in the frontend, if they exist. Specifically: 
* interface_description
* peer_description
* interface_disabled

If interface_disabled is true, then the tunnel will not start automatically
at boot time. You can always start (and stop) any tunnel from the web frontend.


As this add-on sets up clients, you are expected to initiate the connections.
If this is not the case you're thinking about, and you want to use this plugin 
to access your Home Assistant over a WireGuard tunnel, make sure you have a 
reasonable value for **peer_persistent_keepalive**


A sample configuration looks like that: IP addresses are provided as a sample

```yaml
connections:
  - interface_name: wg0
    interface_description: A Description 
    interface_disabled: false 
    interface_dns:
      - 10.0.0.10
    interface_private_key: REPLACE_WITH_THE_INTERFACES_PRIVATE_KEY
    interface_address:
      - 10.0.0.2/24
    interface_preup: []
    interface_postup: []
    interface_predown: []
    interface_postdown: []
    peer_description: A Description
    peer_endpoint: '10.0.0.30:22334'
    peer_allowed_ips:
      - 10.0.0.0/24
    peer_public_key: REPLACE_WITH_THE_PEERS_PRIVATE_KEY
    peer_pre_shared_key: REPLACE_WITH_THE_PRESHARED_KEY
    peer_persistent_keep_alive: '25'
  - interface_name: backup
    interface_private_key: REPLACE_WITH_THE_INTERFACES_PRIVATE_KEY
    interface_dns: []
    interface_disabled: true
    interface_address:
      - 10.0.1.1/24
    interface_preup: []
    interface_postup: []
    interface_predown: []
    interface_postdown: []
    peer_endpoint: 'some.host.name:33445'
    peer_description: This is the backup connection
    peer_public_key: REPLACE_WITH_THIS_PEERS_PRIVATE_KEY
    peer_allowed_ips:
      - 10.0.1.0/24
```

1. Save the configuration.
1. Start the "WireGuard Clients" add-on

## Web UI

The Web UI, accessible only from within Home Assistant, allows you to monitor the
status of your tunnels, as well as start and stop them at will. It auto-refreshes every 30 seconds. 

