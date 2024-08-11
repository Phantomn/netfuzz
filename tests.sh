#!/usr/bin/env bash

# Run integration tests
exit_code=$?

COV=1

if [ $COV -eq 1 ]; then
    coverage run -m pytest tests/
else
    pytest tests/
fi

exit_code=$((exit_code + $?))

exit $exit_code
