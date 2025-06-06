# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
# Declare the build argument VARIANT in the global scope, can be overwrite with devcontainer.json build args
ARG VARIANT=3.12
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}-bullseye

# define apt default source
ARG APT_MIRROR_DOMAIN="deb.debian.org"
# define pip default source
ARG PIP_MIRROR_DOMAIN="pypi.org"

# Consume the build argument in the build stage from global scope
ARG VARIANT

# [Option] Install Node.js
ARG INSTALL_NODE="true"
ARG NODE_VERSION="lts/*"
RUN if [ "${INSTALL_NODE}" = "true" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# Uninstall pre-installed tools
# They would conflict with our requirements.txt
RUN pipx uninstall mypy

# .bashrc or .zshrc add mirror site:
# export APT_MIRROR_DOMAIN="mirrors.tuna.tsinghua.edu.cn"
# --- BEGIN: APT China Mirror Configuration ---
# First, ensure apt's sources.list is initialized
RUN apt-get update -y && \
    cp /etc/apt/sources.list /etc/apt/sources.list.bak && \
    sed -i "s|deb.debian.org|${APT_MIRROR_DOMAIN}|g" /etc/apt/sources.list && \
    sed -i "s|security.debian.org|${APT_MIRROR_DOMAIN}|g" /etc/apt/sources.list

# .bashrc or .zshrc add mirror site:
# export PIP_MIRROR_DOMAIN="pypi.tuna.tsinghua.edu.cn"
# --- BEGIN: PIP China Mirror Configuration ---
RUN mkdir -p /etc/pip && \
    echo "[global]" > /etc/pip/pip.conf && \
    echo "index-url = https://${PIP_MIRROR_DOMAIN}/simple" >> /etc/pip/pip.conf && \
    echo "trusted-host = ${PIP_MIRROR_DOMAIN}" >> /etc/pip/pip.conf
# --- END: PIP Mirror Configuration ---

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
   && apt-get -y install --no-install-recommends ffmpeg libpcap-dev

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
COPY requirements*.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements-all-${VARIANT}.txt \
   && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1