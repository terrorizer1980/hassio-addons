# Build arguments
ARG BUILD_ARCH=amd64
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

# For addon
ARG BUILD_FROM=ghcr.io/hassio-addons/base-python/${BUILD_ARCH}:7.1.0
#For testing
#ARG BUILD_FROM=ghcr.io/home-assistant/${BUILD_ARCH}-base-python:3.9-alpine3.14
FROM ${BUILD_FROM}


# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN \
    apk add --no-cache \
        wireguard-tools=1.0.20210424-r0 \
        openresolv=3.12.0-r0 \
	py3-pip=20.3.4-r1 \
# Removed in version 0.4.0
# py3-flask=2.0.1-r0 \
	\
	&& pip3 install \
		--no-cache-dir \
 		flask \
		configparser 

# Copy root filesystem
COPY rootfs /

# Labels
LABEL \
    io.hass.name="WireGuard Clients" \
    io.hass.description="Connect to unlimited fast secure Wireguard tunnels (as a client)" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="s482dcaw <https://github.com/s482dcaw>" \
    org.opencontainers.image.title="WireGuard Clients" \
    org.opencontainers.image.description="Connect to unlimited fast secure Wireguard tunnels (as a client)" \
    org.opencontainers.image.authors="s482dcaw <https://github.com/s482dcaw>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.source="https://github.com/s482dcaw/hassio-addons/wireguard-clients" \
    org.opencontainers.image.documentation="https://github.com/s482dcaw/hassio-addons/wireguard-clients/blob/master/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
