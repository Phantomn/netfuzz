#!/bin/bash

python3 netfuzz/main.py --protocol "ftp" --target_cmdline "/home/phantom/proftpd-1.3.5/bin/sbin/proftpd -d10 -n -c /home/phantom/proftpd-1.3.5/bin/etc/proftpd.conf -S 127.0.0.1 -4" --target_ip "127.0.0.1" --target_port "20021" --username "ftp" --password "ftp" --csv_out "./proftpd.csv" --sleep_between_cases 0 --tui --text_dump --feature_check
