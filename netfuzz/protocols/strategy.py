from __future__ import annotations

from abc import ABC, abstractmethod

from boofuzz import Session


class Strategy(ABC):
	"""
	Abstract base class for protocol fuzzing strategies.
	"""

	@abstractmethod
	def __init__(self, username: str, password: str):
		"""
		Initialize the protocol strategy with necessary credentials.

		Args:
		    username (str): Username for the protocol.
		    password (str): Password for the protocol.
		"""

	@abstractmethod
	def setup_session(self, session: Session):
		"""
		Set up the protocol commands and establish connections.

		Args:
		    session (Session): The fuzzing session object.
		"""

	@abstractmethod
	def check_reply_code(
		self, target, fuzz_data_logger, session, test_case_context, *args, **kwargs
	):
		"""
		Callback function to check the reply code from the server.

		Args:
			target: The target with a socket-like interface.
		    fuzz_data_logger: Logger for logging fuzzing data.
		    session: The fuzzing session object.
			test_case_context: Context for the test case.
		"""

	@abstractmethod
	def fuzz(self) -> None:
		""" """
