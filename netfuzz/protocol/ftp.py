import logging
import os
import time
import traceback

from boofuzz import Block, Bytes, Delim, Request, Static, String

from netfuzz.core.base import Base


def build_command_request(name, cmd: str, arg=None):
	if arg is None:
		block = Block(name="command", children=[String(name="cmd", default_value=cmd)])
	else:
		block = Block(
			name="Command",
			children=(
				String(name="command", default_value=cmd),
				Delim(name="space", default_value=" "),
				Bytes(name="argument", default_value=arg),
				Static(name="end", default_value="\r\n"),
			),
		)
	return Request(name=name, children=[block])


def build_user(name="user"):
	return build_command_request(name, "USER", b"ftp")


def build_pass(name="pass"):
	return build_command_request(name, "PASS", b"ftp")


def build_pwd(name="pwd"):
	return build_command_request(name, "PWD")


def build_abor(name="abor"):
	return build_command_request(name, "ABOR")


def build_retr(name="retr"):
	return build_command_request(name, "RETR", b"test.txt")


def build_site(name="site"):
	return build_command_request(name, "SITE", b"CHMOD 755 test.txt")


def build_stor(name="stor"):
	return build_command_request(name, "STOR", b"flag.txt")


services_callbacks_dict = {
	"user": build_user,
	"pass": build_pass,
	"pwd": build_pwd,
	"abor": build_abor,
	"retr": build_retr,
	"site": build_site,
	"stor": build_stor,
}


class FTP(Base):
	def __init__(self, target_ip: str, target_port: str) -> None:
		self.target_ip = target_ip
		self.target_port = target_port

		if not os.path.exists("./logs"):
			os.makedirs("./logs")

		logging.basicConfig(
			handlers=[logging.FileHandler(filename=f'./logs/fuzzer_runtime_{time.strftime("%m%d-%H%M%S")}.log', encoding="utf-8", mode="w+")],
			format="%(asctime)s %(message)s",
			level=logging.DEBUG,
		)
		super(FTP, self).__init__(self.target_ip, self.target_port, "ftp", "ftp")

	def _init_protocol_structure(self, cmd="user"):
		try:
			if cmd in services_callbacks_dict:
				request = services_callbacks_dict[cmd](cmd)
				self.session.connect(request)
			else:
				raise ValueError(f"Command '{cmd}' is not supported")
		except Exception as e:
			logging.error(f"protocol structure error: {e} {traceback.format_exc()}")

	def fuzz(self, cmd_seq=None):
		try:
			if not cmd_seq:
				cmd_seq = ["user", "pass", "pwd"]

			self.init()
			for cmd in cmd_seq:
				self._init_protocol_structure(cmd)

			self.session.fuzz()
		except Exception as e:
			logging.error(f"This error happened during fuzz function: {e}")
			logging.error("Resetting session and restarting fuzzing process...")
			self.init()  # 세션 재설정
			self.fuzz(cmd_seq)  # Fuzzing 재시작
