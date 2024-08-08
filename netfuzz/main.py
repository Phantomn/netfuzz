import argparse
from core.fuzzer import Fuzzer
from protocols.ftp import FTP
from utils.log import Logger
import logging

def parse_args():
    parser = argparse.ArgumentParser(description="Network Protocol Fuzzer")
    parser.add_argument('--protocol', type=str, help='Protocol to fuzz')
    parser.add_argument('--address', type=str, help="Target IP")
    return parser.parse_args()

def main():
    args = parse_args()
    
    if args.protocol == 'ftp':
        strategy = FTP(args.address)
    else:
        print(f"Unsupported protocol: {args.protocol}")
        return

    fuzzer = Fuzzer(strategy=strategy)
    fuzzer.run()

if __name__ == "__main__":
    main()
