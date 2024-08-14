from __future__ import annotations

from abc import ABC, abstractmethod


class BooFtpException(Exception):
	pass


class Strategy(ABC):
	"""
	Abstract base class for protocol fuzzing strategies.
	"""

	@abstractmethod
	def __init__(self, username: str, password: str):
		pass

	@abstractmethod
	def setup_session(self):
		pass

	@abstractmethod
	def check_reply_code(self):
		if test_case_context.previous_message.name == "__ROOT_NODE__":
			return
		else:
			try:
				fuzz_data_logger.log_info("Parsing reply contents: {0}".format(session.last_recv))
				parse_ftp_reply(session.last_recv)
			except BooFtpException as e:
				fuzz_data_logger.log_fail(str(e))
			fuzz_data_logger.log_pass()

	@abstractmethod
	def parse_ftp_reply(self):
		pass

	@abstractmethod
	def fuzz(self):
		pass
