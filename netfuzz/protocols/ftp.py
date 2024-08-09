from boofuzz import *
from protocols.strategy import Strategy


class FTP(Strategy):
    def __init__(self, addr):
        self.addr = addr
        self.session = Session(
            target=Target(connection=TCPSocketConnection(self.addr, 21)),
            fuzz_loggers=[
                FuzzLoggerText(file_handle=open("./logs/output.txt", "w")),
                FuzzLoggerCurses(),
            ],
        )

    def define_proto(self):
        user = Request(
            "user",
            children=(
                String(name="key", default_value="USER"),
                Delim(name="space", default_value=" "),
                String(name="val", default_value="phantom"),
                Static(name="end", default_value="\r\n"),
            ),
        )

        passwd = Request(
            "pass",
            children=(
                String(name="key", default_value="PASS"),
                Delim(name="space", default_value=" "),
                String(name="val", default_value="1"),
                Static(name="end", default_value="\r\n"),
            ),
        )

        stor = Request(
            "stor",
            children=(
                String(name="key", default_value="STOR"),
                Delim(name="space", default_value=" "),
                String(name="val", default_value="AAAA"),
                Static(name="end", default_value="\r\n"),
            ),
        )

        retr = Request(
            "retr",
            children=(
                String(name="key", default_value="RETR"),
                Delim(name="space", default_value=" "),
                String(name="val", default_value="AAAA"),
                Static(name="end", default_value="\r\n"),
            ),
        )

        # 명령어 연결 정의
        self.session.connect(user)
        self.session.connect(user, passwd)
        self.session.connect(passwd, stor)
        self.session.connect(passwd, retr)

    def fuzz(self):
        print("Starting FTP fuzzing session")
        self.define_proto()
        try:
            self.session.fuzz()
        except Exception as e:
            print("Fuzzing session crashed", str(e).encode())
            print("Crash saved to database.")
        finally:
            print("FTP fuzzing session completed")
