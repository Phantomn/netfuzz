from __future__ import annotations

import argparse

from netfuzz.core.engine import Engine
from netfuzz.protocol.ftp import FTP


def main() -> None:
	parser = argparse.ArgumentParser(description="Boofuzz 기반 Fuzzing 실행 프로그램")
	parser.add_argument("--protocol", type=str, required=True, help="프로토콜 이름 (예: ftp)")
	parser.add_argument("--target_ip", type=str, required=True, help="대상 장비의 IP 주소")
	parser.add_argument("--target_port", type=int, default=21, help="대상 장비의 포트 번호")
	parser.add_argument("--username", type=str, help="FTP 사용자명")
	parser.add_argument("--password", type=str, help="FTP 비밀번호")
	parser.add_argument("--target_cmdline", type=str, nargs="+", help="대상 명령어")
	parser.add_argument("--test_case_index", type=str, help="테스트 케이스 인덱스")
	parser.add_argument("--test_case_name", type=str, help="테스트 케이스 이름")
	parser.add_argument("--csv_out", type=str, help="CSV 출력 파일 경로")
	parser.add_argument(
		"--sleep_between_cases", type=float, default=0.0, help="테스트 케이스 사이의 대기 시간"
	)
	parser.add_argument("--procmon_host", type=str, help="프로세스 모니터 호스트")
	parser.add_argument("--procmon_port", type=int, help="프로세스 모니터 포트")
	parser.add_argument("--procmon_start", type=str, help="프로세스 시작 명령어")
	parser.add_argument("--procmon_capture", action="store_true", help="프로세스 출력 캡처 여부")
	parser.add_argument("--tui", action="store_true", help="텍스트 사용자 인터페이스 사용 여부")
	parser.add_argument("--text_dump", action="store_true", help="텍스트 덤프 사용 여부")
	parser.add_argument("--feature_check", action="store_true", help="기능 확인 모드 사용 여부")

	args = parser.parse_args()
	protocols = {"ftp": FTP()}

	fuzzer = Engine(protocols)
	fuzzer.run(
		protocol_name=args.protocol.lower(),
		target_cmdline=args.target_cmdline,
		target_host=args.target_ip,
		target_port=args.target_port,
		username=args.username,
		password=args.password,
		test_case_index=args.test_case_index,
		test_case_name=args.test_case_name,
		csv_out=args.csv_out,
		sleep_between_cases=args.sleep_between_cases,
		procmon_host=args.procmon_host,
		procmon_port=args.procmon_port,
		procmon_start=args.procmon_start,
		procmon_capture=args.procmon_capture,
		tui=args.tui,
		text_dump=args.text_dump,
		feature_check=args.feature_check,
	)


if __name__ == "__main__":
	main()
