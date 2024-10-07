from __future__ import annotations

import argparse
import sys

from netfuzz.protocol.ftp import FTP


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("-ti", "--target_ip", type=str, required=True, help="Target IP")
	parser.add_argument("-tp", "--target_port", type=int, required=True, help="Target Port")
	parser.add_argument("-proto", "--target_proto", type=str, required=True, help="Target Protocol")
	args = parser.parse_args()

	if args.target_proto == "ftp":
		fuzzer = FTP(args.target_ip, args.target_port)
	else:
		print(f"Error: Unsupported protocol '{args.target_proto}' specified.")
		sys.exit(1)

	try:
		fuzzer.init()
		fuzzer.fuzz()
	except Exception as e:
		print(f"An error occurred during fuzzing: {e}")
		sys.exit(1)


if __name__ == "__main__":
	main()
