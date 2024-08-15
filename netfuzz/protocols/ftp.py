from __future__ import annotations

from typing import Any, Dict, Tuple

from boofuzz import IFuzzLogger, ProtocolSession, Session, Target

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
			raise BooFtpException(
				"Invalid FTP reply, too short: must be a 3-digit sequence followed by a space"
			)
