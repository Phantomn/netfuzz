from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from boofuzz import IFuzzLogger, ProtocolSession, Session, Target


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
	def setup_session(self, session: Session) -> None:
		pass

	@abstractmethod
	def check_reply_code(
		self,
		target: Target,
		fuzz_data_logger: IFuzzLogger,
		session: Session,
		test_case_context: ProtocolSession,
		*args: Tuple[Any, ...],
		**kwargs: Dict[str, Any],
	) -> None:
		pass

	@abstractmethod
	def parse_ftp_reply(self, data: bytes) -> str:
		pass

	@abstractmethod
	def fuzz(self) -> None:
		pass
