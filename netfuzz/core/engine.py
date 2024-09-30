# Fuzzer 엔진 기능 정의
from __future__ import annotations

from typing import Mapping

from netfuzz.core.base import Base


class Engine:
    """Fuzzer 엔진 클래스"""

    def __init__(self, protocol_modules: Mapping[str, Base]) -> None:
        self.protocol_modules = protocol_modules

    def run(self, protocol_name: str) -> None:
        protocol = self.protocol_modules.get(protocol_name)
        if not protocol:
            raise ValueError(f"지원되지 않는 프로토콜: {protocol_name}")

        protocol.initialize()
        protocol.start()
