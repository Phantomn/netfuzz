#!/usr/bin/env bash
set -e

# If we are a root in a container and `sudo` doesn't exist
# lets overwrite it with a function that just executes things passed to sudo
# (yeah it won't work for sudo executed with flags)
if ! hash sudo 2> /dev/null && whoami | grep -q root; then
    sudo() {
        ${*}
    }
fi

install_apt() {
    sudo apt-get update || true
    sudo apt-get install -y python3.10 python3-dev python3-venv python3-setuptools python-is-python3 curl
}

distro=$(grep "^ID=" /etc/os-release | cut -d'=' -f2 | sed -e 's/"//g')

case $distro in
    "ubuntu")
        install_apt
        ;;
esac

PYVER=$(python -c 'import platform; print(".".join(platform.python_version_tuple()[:2]))')
PYTHON=$(python -c 'import sys; print(sys.executable)')

PYTHON+="${PYVER}"

# Install Poetry
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "Poetry is already installed."
fi

# Create the Python virtual environment and install dependencies using poetry
if [[ -z "${NETFUZZ_VENV_PATH}" ]]; then
    NETFUZZ_VENV_PATH="./.venv"
fi

${PYTHON} -m venv -- ${NETFUZZ_VENV_PATH}
source ${NETFUZZ_VENV_PATH}/bin/activate
poetry install

if uname | grep -iqs Linux; then
    distro=$(grep "^ID=" /etc/os-release | cut -d '=' -f2 | sed -e 's/"//g')

    case $distro in
        "ubuntu")
            install_apt
            ;;
    esac
fi
