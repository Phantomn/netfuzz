# Fuzzer 엔진 기능 정의
from __future__ import annotations

from boofuzz import FuzzLoggerCsv, FuzzLoggerCurses, FuzzLoggerText, Session, Target, TCPSocketConnection
from boofuzz.monitors import ProcessMonitor
from boofuzz.utils.debugger_thread_simple import DebuggerThreadSimple
from boofuzz.utils.process_monitor_local import ProcessMonitorLocal


class Engine:
	def __init__(self, protocols: dict) -> None:
		self.protocols = protocols

	def run(self, protocol_name: str, **kwargs) -> None:
		if protocol_name not in self.protocols:
			raise ValueError(f"지원되지 않는 프로토콜: {protocol_name}")

		protocol = self.protocols[protocol_name]

		session = self.setup_session(kwargs)
		protocol.initialize(session)

		session.fuzz()

	def setup_session(self, kwargs):
		connection = TCPSocketConnection(kwargs["target_host"], kwargs["target_port"])
		monitors = self.setup_monitors(kwargs)
		fuzz_loggers = self.setup_loggers(kwargs)

		index_start = kwargs.get("test_case_index", 1)
		index_start = int(index_start) if index_start is not None else 1
		return Session(
			target=Target(connection=connection, monitors=monitors),
			fuzz_loggers=fuzz_loggers,
			sleep_time=kwargs.get("sleep_between_cases", 0.0),
			index_start=index_start,
			index_end=kwargs.get("test_case_name", None),
			reuse_target_connection=True,
		)

	def setup_monitors(self, kwargs):
		monitors = []
		local_procmon = None

		if len(kwargs["target_cmdline"]) > 0 and kwargs["procmon_host"] is None:
			local_procmon = ProcessMonitorLocal(crash_filename="boofuzz-crash-bin", proc_name=None, pid_to_ignore=None, debugger_class=DebuggerThreadSimple, level=10)

		if isinstance(kwargs["target_cmdline"], list):
			kwargs["target_cmdline"] = " ".join(kwargs["target_cmdline"])

		print(f"DEBUG: target_cmdline = {kwargs['target_cmdline']}")

		procmon_options = {}
		if kwargs["procmon_start"] is not None:
			procmon_options["start_commands"] = kwargs["procmon_start"].split(" ")
		if kwargs["target_cmdline"] is not None:
			procmon_options["start_commands"] = [kwargs["target_cmdline"].split(" ")]
		if kwargs["procmon_capture"]:
			procmon_options["capture_output"] = True

		if local_procmon is not None or kwargs["procmon_host"] is not None:
			if kwargs["procmon_host"] is not None:
				procmon = ProcessMonitor(kwargs["procmon_host"], kwargs["procmon_port"])
			else:
				procmon = local_procmon

			procmon.set_options(**procmon_options)  # type: ignore
			monitors.append(procmon)
		else:
			procmon = None
			monitors = []

		return monitors

	def setup_loggers(self, kwargs):
		fuzz_loggers = []

		if kwargs["text_dump"]:
			fuzz_loggers.append(FuzzLoggerText())
		elif kwargs["tui"]:
			fuzz_loggers.append(FuzzLoggerCurses())

		if kwargs["csv_out"]:
			f = open(kwargs["csv_out"], "w")
			fuzz_loggers.append(FuzzLoggerCsv(file_handle=f))

		return fuzz_loggers
