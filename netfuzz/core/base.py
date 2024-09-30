# 프로토콜 기본 클래스 정의
from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from boofuzz import Session


class Base(ABC):
    def __init__(self, protocol_name: str, target_ip: str, target_port: int) -> None:
        self.protocol_name = protocol_name
        self.target_ip = target_ip
        self.target_port = target_port
        self.session = Session(target=(target_ip, target_port))

    @abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError

    def start(self) -> None:
        self.session.fuzz()
