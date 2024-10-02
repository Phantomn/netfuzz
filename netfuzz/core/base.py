# 프로토콜 기본 클래스 정의
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class Base(ABC):
	def __init__(self, protocol_name: str) -> None:
		self.protocol_name = protocol_name

	@abstractmethod
	def initialize(self) -> None:
		raise NotImplementedError

	@abstractmethod
	def generate_packet(self, cmd: str, arg: Optional[str] = None):
		raise NotImplementedError
