#!/bin/bash

python3 netfuzz/main.py -ti 127.0.0.1 -tp 20021 -proto ftp
