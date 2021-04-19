#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Third Party Add-on: WireGuard Clients
# Creates the interface configuration
# ==============================================================================

declare -a connections=()
declare exlen=0
declare interface=""
declare interface_description=""
declare config=""
declare additional=""
declare private_key=""

declare peer_description=""
declare peer_public_key=""
declare pre_shared_key=""
declare endpoint=""
declare keep_alive=""

declare -a list=()
declare len=0
declare f_value=""
declare temp=""

#if ! bashio::fs.directory_exists '/ssl/wireguard_clients'; then
#    mkdir -p /ssl/wireguard_clients ||
#        bashio::exit.nok "Could not create wireguard storage folder!"
#fi

# Status API Storage
#if ! bashio::fs.directory_exists '/var/lib/wireguard_clients'; then
#    mkdir -p /var/lib/wireguard_clients \
#        || bashio::exit.nok "Could not create status API storage folder"
#fi


# Get config file 

connections=$(jq --raw-output -c -M '.connections' '/data/options.json')
exlen=$(jq --raw-output -c -M 'length' <<< ${connections})

for (( EXCOUNTER=0; EXCOUNTER<${exlen}; EXCOUNTER+=1 )); do
    connection=$(jq --raw-output -c -M '.'[$EXCOUNTER] <<< ${connections})

	if ! bashio::jq.has_value "${connection}" '.interface_name'; then
		bashio::exit.nok 'You need an interface name to set up'
	else
		interface=$(bashio::jq "${connection}" '.interface_name')
    		bashio::log.info "Interface ${interface} being set up!"
		config="/etc/wireguard/${interface}.conf"
		additional="/etc/wireguard/${interface}.comments"
	fi

	###########################
	# Interface configuration #
	###########################
	# Start creation of configuration
	echo "[Interface]" > "${config}"

    # Single entries
	# Check if private key value and if true get the interface private key
	if ! bashio::jq.has_value "${connection}" '.interface_private_key'; then
		bashio::exit.nok 'You need a private_key configured for the interface client'
	else
		private_key=$(bashio::jq "${connection}" '.interface_private_key')
		echo "PrivateKey = ${private_key}" >> "${config}"
	fi

    # Arrays
    #
    # Add all server DNS addresses to the configuration
    list=()
    len=0
    f_value=""
    temp=""
    if ! bashio::jq.is_array "${connection}" '.interface_dns'; then
        bashio::log.warning "You do not have a valid DNS configuration for ${interface}"
    else
        len=$(jq --raw-output -c -M '.interface_dns|length' <<< ${connection})
        for (( COUNTER=0; COUNTER<${len}; COUNTER+=1 )); do
            temp=$(jq --raw-output -c -M '.interface_dns'[$COUNTER] <<< ${connection})
            list+=("${temp}")
        done

        if [ ${#list[@]} -ge 0 ]; then
            f_value=$(IFS=", "; echo "${list[*]}")
            echo "DNS = ${f_value}" >> "${config}"
        fi
    fi

    # Add all addresses to the configuration
    list=()
    len=0
    f_value=""
    temp=""
    if ! bashio::jq.is_array "${connection}" '.interface_address'; then
		bashio::exit.nok "You need at least one address configured for ${interface}"
    else
        len=$(jq --raw-output -c -M '.interface_address|length' <<< ${connection})
        for (( COUNTER=0; COUNTER<${len}; COUNTER+=1 )); do
            temp=$(jq --raw-output -c -M '.interface_address'[$COUNTER] <<< ${connection})
            list+=("${temp}")
        done

        if [ ${#list[@]} -ge 0 ]; then
            f_value=$(IFS=", "; echo "${list[*]}")
            echo "Address = ${f_value}" >> "${config}"
        fi
    fi

    # Add preup commands to the configuration
    # One line per command
    len=0
    f_value=""
    temp=""
    if ! bashio::jq.is_array "${connection}" '.interface_preup'; then
        bashio::log.warning "You do not have a valid PreUp configuration for ${interface}"
    else
        len=$(jq --raw-output -c -M '.interface_preup|length' <<< ${connection})
        for (( COUNTER=0; COUNTER<${len}; COUNTER+=1 )); do
            temp=$(jq --raw-output -c -M '.interface_preup'[$COUNTER] <<< ${connection})
            echo "PreUp = ${temp}" >> "${config}"
        done
    fi

    # Add postup commands to the configuration
    # One line per command
    len=0
    f_value=""
    temp=""
    if ! bashio::jq.is_array "${connection}" '.interface_postup'; then
        bashio::log.warning "You do not have a valid PostUp configuration for ${interface}"
    else
        len=$(jq --raw-output -c -M '.interface_postup|length' <<< ${connection})
        for (( COUNTER=0; COUNTER<${len}; COUNTER+=1 )); do
            temp=$(jq --raw-output -c -M '.interface_postup'[$COUNTER] <<< ${connection})
            echo "PostUp = ${temp}" >> "${config}"
        done
    fi

    # Add predown commands to the configuration
    # One line per command
    len=0
    f_value=""
    temp=""
    if ! bashio::jq.is_array "${connection}" '.interface_predown'; then
        bashio::log.warning "You do not have a valid PreDown configuration for ${interface}"
    else
        len=$(jq --raw-output -c -M '.interface_predown|length' <<< ${connection})
        for (( COUNTER=0; COUNTER<${len}; COUNTER+=1 )); do
            temp=$(jq --raw-output -c -M '.interface_predown'[$COUNTER] <<< ${connection})
            echo "PreDown = ${temp}" >> "${config}"
        done
    fi

    # Add postdown commands to the configuration
    # One line per command
    len=0
    f_value=""
    temp=""
    if ! bashio::jq.is_array "${connection}" '.interface_postdown'; then
        bashio::log.warning "You do not have a valid PostDown configuration for ${interface}"
    else
        len=$(jq --raw-output -c -M '.interface_postdown|length' <<< ${connection})
        for (( COUNTER=0; COUNTER<${len}; COUNTER+=1 )); do
            temp=$(jq --raw-output -c -M '.interface_postdown'[$COUNTER] <<< ${connection})
            echo "PostDown = ${temp}" >> "${config}"
        done
    fi


    # Additional
	echo "[Interface]" > "${additional}"

	# Check if description and if true write it in additional
	if bashio::jq.has_value "${connection}" '.interface_description'; then
		interface_description=$(bashio::jq "${connection}" '.interface_description')
		echo "Description = ${interface_description}" >> "${additional}"
	fi


	######################
	# Peer configuration #
	######################
	# Start creation of configuration
	echo "" >> "${config}"
	echo "[Peer]" >> "${config}"
	# Check if public key value and if true get the peer public key
	if ! bashio::jq.has_value "${connection}" '.peer_public_key'; then
		bashio::exit.nok 'You need a public_key configured for the peer'
	else
		peer_public_key=$(bashio::jq "${connection}" '.peer_public_key')
		echo "PublicKey = ${peer_public_key}" >> "${config}"
	fi

	# Check if endpoint value and if true get the peer endpoint
	if ! bashio::jq.has_value "${connection}" '.peer_endpoint'; then
        bashio::exit.nok 'You need a endpoint configured for the peer'
	else
        endpoint=$(bashio::jq "${connection}" '.peer_endpoint')
		echo "Endpoint = ${endpoint}" >> "${config}"
	fi

	# Check if pre_shared key value and if true get the peer pre_shared key
	# Otherwise proceed without pre-shared key
	if bashio::jq.has_value "${connection}" '.peer_pre_shared_key'; then
		pre_shared_key=$(bashio::jq "${connection}" '.peer_pre_shared_key')
		echo "PreSharedKey = ${pre_shared_key}" >> "${config}"
    else
		bashio::log.warning "You do not have PreSharedKey for connecting ${interface} with endpoint ${endpoint}"
	fi

	# Check if persistent_keep_alive value and if true get the peer persistent_keep_alive
	# Otherwise proceed without persistent keep alive
	if bashio::jq.has_value "${connection}" '.peer_persistent_keep_alive'; then
		keep_alive=$(bashio::jq "${connection}" '.peer_persistent_keep_alive')
		echo "PersistentKeepalive = ${keep_alive}" >> "${config}"
    else
		bashio::log.warning "You do not have PersistentKeepalive setting for ${interface} with endpoint ${endpoint}"
	fi

    # Add allowed IPs for this tunnel
    list=()
    len=0
    f_value=""
    temp=""
    if ! bashio::jq.is_array "${connection}" '.peer_allowed_ips'; then
		bashio::exit.nok "You need at least one AllowedIPs entry for this tunnel"
    else
        len=$(jq --raw-output -c -M '.peer_allowed_ips|length' <<< ${connection})
        for (( COUNTER=0; COUNTER<${len}; COUNTER+=1 )); do
            temp=$(jq --raw-output -c -M '.peer_allowed_ips'[$COUNTER] <<< ${connection})
            list+=("${temp}")
        done

        if [ ${#list[@]} -ge 0 ]; then
            f_value=$(IFS=", "; echo "${list[*]}")
            echo "AllowedIPs = ${f_value}" >> "${config}"
        fi
    fi


    # Additional
	echo "" >> "${additional}"
	echo "[Peer]" >> "${additional}"

	# Check if description and if true write it in additional
	if bashio::jq.has_value "${connection}" '.peer_description'; then
		peer_description=$(bashio::jq "${connection}" '.peer_description')
		echo "Description = ${peer_description}" >> "${additional}"
	fi

	echo ""

	bashio::log.info "Ended writing Wireguard configuration for interface [${interface}] into: [${config}]"
done

bashio::log.info "Finished writing configuration files"
