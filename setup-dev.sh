#!/usr/bin/env bash
set -e

echo "# --------------------------------------"
echo "# Install testing tools."
echo "# Only works with Ubuntu / APT."
echo "# --------------------------------------"

hook_script_path=".git/hooks/pre-push"
hook_script=$(
    cat << 'EOF'
#!/usr/bin/env bash

diff_command="git diff --no-ext-diff --ignore-submodules"

old_diff=$($diff_command)

./lint.sh -f
exit_code=$?

new_diff=$($diff_command)

if [[ "$new_diff" != "$old_diff" ]]; then
   echo "Files were modified by the linter, amend your commit and try again"
   exit 1
fi

exit $exit_code
EOF
)

if [ -t 1 ] && [ ! -f $hook_script_path ]; then
    echo "Install a git hook to automatically lint files before pushing? (y/N)"
    read yn
    if [[ "$yn" == [Yy]* ]]; then
        echo "$hook_script" > "$hook_script_path"
        # make the hook executable
        chmod ug+x "$hook_script_path"
        echo "pre-push hook installed to $hook_script_path and made executable"
    fi
fi

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
    sudo apt-get install -y \
        libc6-dev \
        curl \
        build-essential

    if [[ "$1" != "" && "$1" != "20.04" ]]; then
        sudo apt install shfmt
    fi

    command -v go &> /dev/null || sudo apt-get install -y golang
}

if uname | grep -iqs Linux; then
    distro=$(grep "^ID=" /etc/os-release | cut -d '=' -f2 | sed -e 's/"//g')

    case $distro in
        "ubuntu")
            ubuntu_version=$(grep "^VERSION_ID=" /etc/os-release | cut -d '=' -f2 | sed -e 's/"//g')
            install_apt $ubuntu_version
            ;;
    esac

    if [[ -z "${NETFUZZ_VENV_PATH}" ]]; then
        NETFUZZ_VENV_PATH="./.venv"
    fi
    echo "Using virtualenv from path: ${NETFUZZ_VENV_PATH}"

    source "${NETFUZZ_VENV_PATH}/bin/activate"
    $HOME/.local/bin/poetry install --with dev

    # Create a developer marker file
    DEV_MARKER_PATH="${NETFUZZ_VENV_PATH}/dev.marker"
    touch "${DEV_MARKER_PATH}"
    echo "Developer marker created at ${DEV_MARKER_PATH}"
fi
