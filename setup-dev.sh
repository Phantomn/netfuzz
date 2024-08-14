#!/usr/bin/env bash
set -e

# Git pre-push 훅 설치
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
if [ ! -d ".git/hooks" ]; then
    echo "Creating .git/hooks directory..."
    mkdir -p .git/hooks
fi

if [ ! -f "$hook_script_path" ]; then
    echo "Installing pre-push git hook..."
    echo "$hook_script" > "$hook_script_path"
    chmod ug+x "$hook_script_path"
    echo "pre-push hook installed to $hook_script_path and made executable"
fi

DEV_MARKER_PATH="${NETFUZZ_VENV_PATH}/dev.marker"
touch "${DEV_MARKER_PATH}"
echo "Developer marker created at ${DEV_MARKER_PATH}"
