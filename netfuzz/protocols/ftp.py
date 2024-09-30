from __future__ import annotations

import re
from typing import Any, Dict, Tuple

from boofuzz import Delim, IFuzzLogger, ProtocolSession, Request, Session, Static, String, Target

from netfuzz.protocols.strategy import BooFtpException, Strategy


class FTP(Strategy):
	def __init__(self, username: str, password: str):
		self.username = username
		self.password = password
		self.session = None

	def check_reply_code(
		self,
		target: Target,
		fuzz_data_logger: IFuzzLogger,
		session: Session,
		test_case_context: ProtocolSession,
		*args: Tuple[Any, ...],
		**kwargs: Dict[str, Any],
	) -> None:
		if test_case_context.previous_message.name == "__ROOT_NODE__":
			return
		self.handle_reply(session, fuzz_data_logger)

	def handle_reply(self, session: Session, fuzz_data_logger: IFuzzLogger) -> None:
		try:
			fuzz_data_logger.log_info(f"Parsing reply contents: {session.last_recv}")
			reply_code = self.parse_ftp_reply(session.last_recv)
			fuzz_data_logger.log_pass()
		except BooFtpException as e:
			fuzz_data_logger.log_fail(str(e))

	def parse_ftp_reply(self, data: bytes) -> str:
		reply_code_len = 3
		if len(data) < reply_code_len:
			raise BooFtpException("Invalid FTP reply, too shortl must be a 3-digit")

		try:
			reply = data[0 : reply_code_len + 1].decode("ascii")
		except ValueError:
			raise BooFtpException("Invalid FTP reply, non-ASCII chars; must be a 3-digit")

		if not re.match(r"[1-5][0-9][0-9] ", reply[0:4]):
			raise BooFtpException("Invalid FTP reply; must be a 3-digit")

		return reply[0:reply_code_len]

	def setup_session(self, session: Session) -> None:
		user = self._ftp_1_arg(cmd_code="USER", default_value=self.username)
		password = self._ftp_1_arg(cmd_code="PASS", default_value=self.password)
		stor = self._ftp_1_arg(cmd_code="STOR", default_value="AAAA")
		retr = self._ftp_1_arg(cmd_code="RETR", default_value="AAAA")
		mkd = self._ftp_1_arg(cmd_code="MKD", default_value="AAAA")
		abor = self._ftp_0_arg(cmd_code="ABOR")

		session.connect(user, callback=self.check_reply_code)
		session.connect(user, password, callback=self.check_reply_code)
		session.connect(password, stor, callback=self.check_reply_code)
		session.connect(password, retr, callback=self.check_reply_code)
		session.connect(password, mkd, callback=self.check_reply_code)
		session.connect(password, abor, callback=self.check_reply_code)
		session.connect(stor, abor, callback=self.check_reply_code)
		session.connect(retr, abor, callback=self.check_reply_code)
		session.connect(mkd, abor, callback=self.check_reply_code)

	def _ftp_0_arg(self, cmd_code: str) -> Request:
		return Request(
			cmd_code.lower(),
			children=(
				String(name="key", default_value=cmd_code),
				Static(name="end", default_value="\r\n"),
			),
		)

	def _ftp_1_arg(self, cmd_code: str, default_value: str) -> Request:
		return Request(
			cmd_code.lower(),
			children=(
				String(name="key", default_value=cmd_code),
				Delim(name="sep", default_value=" "),
				String(name="value", default_value=default_value),
				Static(name="end", default_value="\r\n"),
			),
		)

	def fuzz(self) -> None:
		print("FTP Fuzzing in progress...")
