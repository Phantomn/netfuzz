from __future__ import annotations

import os
import random
from typing import Optional

from boofuzz import Block, Delim, Request, Session, Static, String
from pyradamsa import Radamsa

from netfuzz.core.base import Base


class State:
	def __init__(self) -> None:
		self.state = "INITIAL"
		self.rules = {
			"INITIAL": {"USER": "WAIT_PASS"},
			"WAIT_PASS": {"PASS": "AUTHENTICATED"},
			"AUTHENTICATED": {
				"CWD": "AUTHENTICATED",
				"MKD": "AUTHENTICATED",
				"RMD": "AUTHENTICATED",
				"DELE": "AUTHENTICATED",
				"RETR": "DATA_TRANSFER",
				"STOR": "DATA_TRANSFER",
				"RNFR": "WAIT_RNTO",
				"QUIT": "INITIAL",
				"SITE": "AUTHENTICATED",
				"STAT": "AUTHENTICATED",
				"HELP": "AUTHENTICATED",
			},
			"WAIT_RNTO": {"RNTO": "AUTHENTICATED"},
			"DATA_TRANSFER": {"ABOR": "AUTHENTICATED"},
		}

	def get_next_state(self, command: str) -> str:
		return self.rules.get(self.state, {}).get(command, "INVALID")

	def update_state(self, command: str) -> None:
		next_state = self.get_next_state(command)
		if next_state != "INVALID":
			print(f"State changed: {self.state} -> {next_state}")
			self.state = next_state
		else:
			print(f"Invalid state transition: {self.state} with command {command}")


class FTP(Base):
	def __init__(self) -> None:
		super().__init__("FTP")
		self.path = "/home/phantom"
		self.command = [
			("USER", "ftp"),  # 사용자 이름
			("PASS", "ftp"),  # 비밀번호
			("PWD", None),  # 현재 디렉토리 확인
			("CWD", "/tmp/test"),  # 디렉토리 변경
			("MKD", "/tmp/test2"),  # 디렉토리 생성
			("DELE", "test.txt"),  # 파일 삭제
			("RMD", "/tmp/test"),  # 디렉토리 삭제
			("ABOR", None),  # 전송 중단
			("RETR", "test.txt"),  # 파일 다운로드
			("RNFR", "rename.txt"),  # 파일 이름 변경 (원본 이름)
			("RNTO", "new_rename.txt"),  # 파일 이름 변경 (새 이름)
			("SITE", "CHMOD 755 test.txt"),  # 사이트별 명령어 전달
			("STOR", "upload_file.txt"),  # 파일 업로드
			("QUIT", None),  # FTP 세션 종료
		]
		self.state = State()
		self.radamsa = Radamsa()
		self.update_commands_with_files()

	def initialize(self, session: Session) -> None:
		previous_request = None
		for cmd, arg in self.command:
			if self.state.state == "INITIAL" and cmd == "USER":
				dynamic_arg = self.generate_radamsa_argument(cmd, arg, 1.5, 42)
				req = self.generate_packet(cmd, dynamic_arg)
				session.connect(session.root, req)
				previous_request = req
				self.state.update_state(cmd)
				break

		# 이후 상태 전이에 따른 명령어 연결
		for cmd, arg in self.command:
			if self.state.get_next_state(cmd) != "INVALID":
				# pyradamsa를 사용하여 변형된 인자 생성
				dynamic_arg = self.generate_radamsa_argument(cmd, arg, 1.0, random.randint(0, 1000))
				req = self.generate_packet(cmd, dynamic_arg)
				session.connect(previous_request, req)
				self.state.update_state(cmd)
				previous_request = req

	def generate_radamsa_argument(
		self, cmd: str, base_value: Optional[str], ratio: float, seed: Optional[int]
	) -> str:
		if base_value is None:
			base_value = "default"

		radamsa_options = {"ratio": ratio}
		if seed is not None:
			radamsa_options["seed"] = seed

		if cmd == "CWD":
			mutated_value = self.radamsa.fuzz(
				f"/tmp/../home/{random.randint(1, 100)}".encode(), **radamsa_options
			)
		elif cmd in ["RETR", "STOR"]:
			mutated_value = self.radamsa.fuzz(
				f"file_{random.randint(1, 100)}.txt".encode(), **radamsa_options
			)
		elif cmd == "SITE":
			mutated_value = self.radamsa.fuzz(
				f"CHMOD {random.randint(400, 755)}; ls -al".encode(), **radamsa_options
			)
		elif cmd in ["RNFR", "RNTO"]:
			mutated_value = self.radamsa.fuzz(
				f"rename_{random.randint(1, 100)}.txt".encode(), **radamsa_options
			)
		else:
			mutated_value = self.radamsa.fuzz(base_value.encode(), **radamsa_options)

		return mutated_value.decode("utf-8")

	def generate_packet(self, cmd: str, arg: Optional[str] = None) -> Request:
		if arg is None:
			block = Block(name="Command", children=[String(name="command", default_value=cmd)])
		else:
			block = Block(
				name="Command",
				children=(
					String(name="command", default_value=cmd),
					Delim(name="space", default_value=" ") if arg else None,
					String(name="argument", default_value=arg) if arg else None,
				),
			)

		return Request(name=cmd.lower(), children=(block, Static(name="end", default_value="\r\n")))

	def scan_directory_files(self) -> list[str]:
		if not os.path.isdir(self.path):
			raise ValueError(f"유효하지 않은 디렉토리 경로: {self.path}")
		return [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]

	def update_commands_with_files(self) -> None:
		files = self.scan_directory_files()
		command_dict = dict(self.command)

		command_dict.update(
			{
				"RETR": files[0] if files else "default.txt",  # 첫 번째 파일로 다운로드 테스트
				"STOR": "upload_file.txt",  # 업로드할 파일
				"RNFR": files[0] if files else "default.txt",  # 이름 변경할 원본 파일
				"RNTO": "renamed_file.txt",
			}
		)
		self.command = list(command_dict.items())
