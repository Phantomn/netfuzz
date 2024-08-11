from __future__ import annotations


class Fuzzer:
    def __init__(self, strategy):
        self.strategy = strategy

    def run(self):
        print("Fuzzing 시작")
        self.strategy.fuzz()
        print("Fuzzing 종료")
