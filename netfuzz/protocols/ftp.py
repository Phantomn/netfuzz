from __future__ import annotations

import re

from boofuzz import Delim
from boofuzz import Request
from boofuzz import Session
from boofuzz import Static
from boofuzz import String

from netfuzz.protocols.strategy import Strategy


class BooFtpException(Exception):
    pass


class FTP(Strategy):
    def __init__(self, username: str, password: str):
        """
        Initialize FTP strategy with username and password.

        Args:
            username (str): FTP username.
            password (str): FTP password.
        """
        self.username = username
        self.password = password

    def setup_session(self, session: Session):
        """
        Define FTP protocol commands and establish connections.

        Args:
            session (Session): The fuzzing session object.
        """
        user = self._ftp_cmd_1_arg(cmd_code="USER", default_value=self.username)
        password = self._ftp_cmd_1_arg(cmd_code="PASS", default_value=self.password)
        stor = self._ftp_cmd_1_arg(cmd_code="STOR", default_value="AAAA")
        retr = self._ftp_cmd_1_arg(cmd_code="RETR", default_value="AAAA")
        mkd = self._ftp_cmd_1_arg(cmd_code="MKD", default_value="AAAA")
        abor = self._ftp_cmd_0_arg(cmd_code="ABOR")

        # Establish connections with callback for reply code check
        session.connect(user, callback=self.check_reply_code)
        session.connect(user, password, callback=self.check_reply_code)
        session.connect(password, stor, callback=self.check_reply_code)
        session.connect(password, retr, callback=self.check_reply_code)
        session.connect(password, mkd, callback=self.check_reply_code)
        session.connect(password, abor, callback=self.check_reply_code)
        session.connect(stor, abor, callback=self.check_reply_code)
        session.connect(retr, abor, callback=self.check_reply_code)
        session.connect(mkd, abor, callback=self.check_reply_code)

    def check_reply_code(
        self, target, fuzz_data_logger, session, test_case_context, *args, **kwargs
    ):
        """
        Callback function to check the reply code from the FTP server.
        """
        if test_case_context.previous_message.name == "__ROOT_NODE__":
            return
        try:
            fuzz_data_logger.log_info(f"Parsing reply contents: {session.last_recv}")
            self.parse_ftp_reply(session.last_recv)
        except BooFtpException as e:
            fuzz_data_logger.log_fail(str(e))
        fuzz_data_logger.log_pass()

    @staticmethod
    def parse_ftp_reply(data):
        """
        Parse FTP reply and return reply code.
        Raise BooFtpException if reply is invalid.
        """
        reply_code_len = 3
        if len(data) < reply_code_len:
            raise BooFtpException(
                "Invalid FTP reply: must 3 digit & space, not non-ASCII"
            )
        try:
            reply = data[0 : reply_code_len + 1].decode("ascii")
        except ValueError:
            raise BooFtpException(
                "Invalid FTP reply: must 3 digit & space, not non-ASCII"
            )
        if not re.match("[1-5][0-9][0-9] ", reply[0:4]):
            raise BooFtpException("Invalid FTP reply: must 3 digit & space")
        return reply[0:reply_code_len]

    @staticmethod
    def _ftp_cmd_0_arg(cmd_code):
        """
        Define an FTP command with no arguments.
        """
        return Request(
            cmd_code.lower(),
            children=(
                String(name="key", default_value=cmd_code),
                Static(name="end", default_value="\r\n"),
            ),
        )

    @staticmethod
    def _ftp_cmd_1_arg(cmd_code, default_value):
        """
        Define an FTP command with one argument.
        """
        return Request(
            cmd_code.lower(),
            children=(
                String(name="key", default_value=cmd_code),
                Delim(name="sep", default_value=" "),
                String(name="value", default_value=default_value),
                Static(name="end", default_value="\r\n"),
            ),
        )
