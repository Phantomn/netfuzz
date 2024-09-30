#!/bin/bash

python3 netfuzz/main.py --protocol "ftp" --target_cmdline "" --target_ip "192.168.11.102" --target_port "21" --username "ftp" --password "ftp" --csv_out "./proftpd.csv" --sleep_between_cases 1 --tui --text_dump --feature_check
