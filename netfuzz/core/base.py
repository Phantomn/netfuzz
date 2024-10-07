from __future__ import annotations

import logging

from boofuzz import ProcessMonitorLocal, Session, Target, TCPSocketConnection
from boofuzz.utils.debugger_thread_simple import DebuggerThreadSimple


class Base:
	def __init__(self, target_ip: str, target_port: str, protocol: str, packet_name: str) -> None:
		self.protocol = protocol
		self.target_ip = target_ip
		self.target_port = target_port
		self.packet_name = packet_name
		try:
			start_command = ["service", "proftpd", "start"]
			stop_command = ["service", "proftpd", "stop"]
			procmon = ProcessMonitorLocal(
				crash_filename=f"{self.packet_name}.bin",
				proc_name="proftpd",
				pid_to_ignore=None,
				debugger_class=DebuggerThreadSimple,
				level=10,
				start_commands=[start_command],
				stop_commands=[stop_command],
			)
			self.session = Session(
				target=Target(connection=TCPSocketConnection(self.target_ip, self.target_port), monitors=[procmon]),
				restart_threshold=1,
				ignore_connection_reset=True,
				fuzz_db_keep_only_n_pass_cases=1000,
				index_end=None,
			)
		except Exception as e:
			logging.error(f"connection Error: {e}")

	def _init_protocol_structure(self, cmd):
		raise NotImplementedError

	def init(self):
		self._init_protocol_structure(cmd="user")

	def fuzz(self):
		if not self.session:
			raise Exception("Session is not initialized. Call `init()` before `fuzz()`.")

		self.session.fuzz()
