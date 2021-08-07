# 0.4.0 
- Major change: The interfaces can be marked as disabled so they don't start on boot. Read the documentation for configuration information
- Major change: You can now start / stop the interfaces from the web frontend. This does not change the configuration which is read on boot time
- Bump base image to base-python 7.10
- Bump wireguard to wireguard-tools-1.0.20210424-r0
- Installing now flask through pip3 
- Remove jq.sh as it is now fixed upstream

# 0.3.2 
- Differentiate between started and connected

# 0.3.1 
- Documentation corrections
- Seperate license file
- Screenshot for better understanding of what it provides

# 0.3.0 
- Modified the configuration to allow all valid options
- Added monitoring frontend inspired by https://github.com/donaldzou/wireguard-dashboard

# 0.2.0
- Forked from https://github.com/bigmoby/addon-wireguard-client
- Added the ability to have multiple wg interfaces
- Cleaned up configuration by removing erroneous postup / postdown and making non-mandatory options write a log, instead of stopping the addon
