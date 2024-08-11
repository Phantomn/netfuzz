#!/bin/bash

# setup.sh

echo "Setting up the project environment..."

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Lint code
poetry run flake8 netfuzz

# Cleanup
find . -type f -name '*.pyc' -delete
find . -type d -name '__pycache__' -exec rm -r {} +

echo "Setup complete!"

