from utils.log import Logger

class Fuzzer:
    def __init__(self, strategy):
        self.strategy = strategy
        self.logger = Logger.getLogger()

    def run(self):
        self.logger.info("Fuzzing 시작")
        self.strategy.fuzz()
        self.logger.info("Fuzzing 종료")
