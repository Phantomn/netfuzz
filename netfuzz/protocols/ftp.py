from boofuzz import Session, Target, s_initialize, s_string, s_static, s_get
from protocols.strategy import Strategy
from utils.log import Logger

class FTP(Strategy):
    def __init__(self, addr):
        self.logger = Logger.getLogger()
        self.addr = addr
    def fuzz(self):
        self.logger.info("Initializing FTP fuzzing session")
        session = Session(target=Target(connection=(self.addr, 21)))

        s_initialize("USER")
        s_static("USER")
        s_string("anonymous")
        s_static("\r\n")

        s_initialize("PASS")
        s_static("PASS")
        s_string("password")
        s_static("\r\n")

        session.connect(s_get("USER"))
        session.connect(s_get("PASS"))

        self.logger.info("Starting FTP fuzzing")
        session.fuzz()
        self.logger.info("FTP fuzzing completed")
