from __future__ import annotations

import argparse

from netfuzz.core.engine import Engine
from netfuzz.protocol.ftp import FTP


def main() -> None:
    parser = argparse.ArgumentParser(description="Protocol Fuzzing 실행 프로그램")
    parser.add_argument("--protocol", type=str, required=True, help="프로토콜 이름 (예: FTP)")
    parser.add_argument("--target_ip", type=str, required=True, help="대상 장비의 IP 주소")
    parser.add_argument("--target_port", type=int, default=21, help="대상 장비의 포트 번호 (기본값: 21)")

    args = parser.parse_args()

    # 프로토콜 모듈 초기화
    protocols = {
        "FTP": FTP(args.target_ip, args.target_port),
    }

    fuzzer = Engine(protocols)
    fuzzer.run(args.protocol)


if __name__ == "__main__":
    main()
