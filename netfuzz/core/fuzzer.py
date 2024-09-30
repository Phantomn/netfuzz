from __future__ import annotations

from netfuzz.protocols.strategy import Strategy


class Fuzzer:
	def __init__(self, strategy: Strategy):
		self.strategy = strategy

	def setup(self):
		print("Setting session...")
		self.strategy.setup_session()

	def run(self):
		print("Fuzzing 시작")
		self.strategy.fuzz()
		print("Fuzzing 종료")
