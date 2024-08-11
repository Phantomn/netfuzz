#!/usr/bin/env bash

# Run integration tests
(cd tests/ && python3 tests.py $@)
exit_code=$?

COV=0
# Run unit tests
for arg in "$@"; do
    if [ "$arg" == "--cov" ]; then
        COV=1
        break
    fi
done

if [ $COV -eq 1 ]; then
    coverage run -m pytest tests/
else
    pytest tests/
fi

exit_code=$((exit_code + $?))

exit $exit_code
