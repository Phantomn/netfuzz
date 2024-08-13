from __future__ import annotations

import re
from typing import Any, Dict, Tuple

from boofuzz import Delim, IFuzzLogger, ProtocolSession, Request, Session, Static, String, Target

from netfuzz.protocols.strategy import Strategy


class BooFtpException(Exception):
	pass


class FTP(Strategy):
	def __init__(self, username: str, password: str):
		"""
		Initialize FTP strategy with username and password.

		Args:
		    username (str): FTP username.
		    password (str): FTP password.
		    target_host (str): Target host for the FTP server.
		    target_port (int): Target port for the FTP server.
		"""
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
	):
		"""
		Args:
		    target (Target): Target with sock-like interface.
		    fuzz_data_logger (ifuzz_logger.IFuzzLogger): Allows logging of test checks and passes/failures.
		        Provided with a test case and test step already opened.
		    session (Session): Session object calling post_send.
		        Useful properties include last_send and last_recv.
		    test_case_context (ProtocolSession): Context for test case-scoped data.
		        :py:class:`TestCaseContext` :py:attr:`session_variables <TestCaseContext.session_variables>`
		        values are generally set within a callback and referenced in elements via default values of type
		        :py:class:`ReferenceValueTestCaseSession`.
		    args: Implementations should include \\*args and \\**kwargs for forward-compatibility.
		    kwargs: Implementations should include \\*args and \\**kwargs for forward-compatibility.
		"""
		if test_case_context.previous_message.name == "__ROOT_NODE__":
			return
		try:
			fuzz_data_logger.log_info(f"Parsing reply contents: {session.last_recv}")
			self.parse_ftp_reply(session.last_recv)
		except BooFtpException as e:
			fuzz_data_logger.log_fail(str(e))
		fuzz_data_logger.log_pass()

	def parse_ftp_reply(self, data: bytes):
		"""
		Parse FTP reply and return reply code. Raise BooFtpException if reply is invalid.

		Note:
		1. Multi-line replies not supported yet

		RFC 959 excerpt:
		    A reply is defined to contain the 3-digit code, followed by Space
		    <SP>, followed by one line of text (where some maximum line length
		    has been specified), and terminated by the Telnet end-of-line
		    code.  There will be cases however, where the text is longer than
		    a single line...

		Args:
		    data (bytes): Raw reply data
		"""
		reply_code_len = 3
		if len(data) < reply_code_len:
			raise BooFtpException(
				"Invalid FTP reply, too short; must be a 3-digit sequence followed by a space"
			)
		try:
			reply = data[0 : reply_code_len + 1].decode("ascii")
		except ValueError:
			raise BooFtpException(
				"Invalid FTP reply, non-ASCII characters; must be a 3-digit sequence followed by a space"
			)
		if not re.match("[1-5][0-9][0-9] ", reply[0:4]):
			raise BooFtpException(
				"Invalid FTP reply; must be a 3-digit sequence followed by a space"
			)
		return reply[0:reply_code_len]

	def setup_session(self, session: Session):
		"""
		RFC 5797:


		2.4.  Base FTP Commands

		The following commands are part of the base FTP specification
		[RFC0959] and are listed in the registry with the immutable pseudo
		FEAT code "base".

		Mandatory commands:

		ABOR, ACCT, ALLO, APPE, CWD, DELE, HELP, LIST, MODE, NLST, NOOP,
		PASS, PASV, PORT, QUIT, REIN, REST, RETR, RNFR, RNTO, SITE, STAT,
		STOR, STRU, TYPE, USER

		"""
		user = self._ftp_cmd_1_arg(cmd_code="USER", default_value=self.username)
		password = self._ftp_cmd_1_arg(cmd_code="PASS", default_value=self.password)
		stor = self._ftp_cmd_1_arg(cmd_code="STOR", default_value="AAAA")
		retr = self._ftp_cmd_1_arg(cmd_code="RETR", default_value="AAAA")
		mkd = self._ftp_cmd_1_arg(cmd_code="MKD", default_value="AAAA")
		abor = self._ftp_cmd_0_arg(cmd_code="ABOR")

		session.connect(user, callback=self.check_reply_code)
		session.connect(user, password, callback=self.check_reply_code)
		session.connect(password, stor, callback=self.check_reply_code)
		session.connect(password, retr, callback=self.check_reply_code)
		session.connect(password, mkd, callback=self.check_reply_code)
		session.connect(password, abor, callback=self.check_reply_code)
		session.connect(stor, abor, callback=self.check_reply_code)
		session.connect(retr, abor, callback=self.check_reply_code)
		session.connect(mkd, abor, callback=self.check_reply_code)

	def _ftp_cmd_0_arg(self, cmd_code: str) -> Request:
		return Request(
			cmd_code.lower(),
			children=(
				String(name="key", default_value=cmd_code),
				Static(name="end", default_value="\r\n"),
			),
		)

	def _ftp_cmd_1_arg(self, cmd_code: str, default_value: str) -> Request:
		return Request(
			cmd_code.lower(),
			children=(
				String(name="key", default_value=cmd_code),
				Delim(name="sep", default_value=" "),
				String(name="value", default_value=default_value),
				Static(name="end", default_value="\r\n"),
			),
		)

	def fuzz(self):
		local_procmon = None
		if len(target_cmdline) > 0 and procmon_host is None:
			local_procmon = ProcessMonitorLocal(
				crash_filename="boofuzz-crash-bin",
				proc_name=None,  # "proftpd",
				pid_to_ignore=None,
				debugger_class=DebuggerThreadSimple,
				level=1,
			)

		fuzz_loggers = []
		if text_dump:
			fuzz_loggers.append(FuzzLoggerText())
		elif tui:
			fuzz_loggers.append(FuzzLoggerCurses())
		if csv_out is not None:
			f = open("ftp-fuzz.csv", "wb")
			fuzz_loggers.append(FuzzLoggerCsv(file_handle=f))

		procmon_options = {}
		if procmon_start is not None:
			procmon_options["start_commands"] = [procmon_start]
		if target_cmdline is not None:
			procmon_options["start_commands"] = [list(target_cmdline)]
		if procmon_capture:
			procmon_options["capture_output"] = True

		if local_procmon is not None or procmon_host is not None:
			if procmon_host is not None:
				procmon = ProcessMonitor(procmon_host, procmon_port)
			else:
				procmon = local_procmon
			procmon.set_options(**procmon_options)
			monitors = [procmon]
		else:
			procmon = None
			monitors = []

		start = None
		end = None
		if test_case_index is None:
			start = 1
		elif "-" in test_case_index:
			start, end = test_case_index.split("-")
			if not start:
				start = 1
			else:
				start = int(start)
			if not end:
				end = None
			else:
				end = int(end)
		else:
			int(test_case_index)

		connection = TCPSocketConnection(target_host, target_port)

		Session(
			target=Target(connection=connection, monitors=monitors),
			fuzz_loggers=fuzz_loggers,
			sleep_time=sleep_between_cases,
			index_start=start,
			index_end=end,
		)
