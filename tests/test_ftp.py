from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from boofuzz import Session

from netfuzz.protocols.ftp import FTP
from netfuzz.protocols.ftp import BooFtpException


class TestFTP(unittest.TestCase):
    def setUp(self):
        """Set up test case environment."""
        self.username = "raspberry"
        self.password = "pi"
        self.ftp = FTP(username=self.username, password=self.password)
        self.session = MagicMock(spec=Session)
        self.session.target = MagicMock()

    def test_initialize(self):
        """Test FTP session initialization."""
        self.ftp.setup_session(self.session)
        # Verify connections are established
        self.assertEqual(self.session.connect.call_count, 9)

    def test_parse_valid_reply(self):
        """Test parsing a valid FTP reply."""
        reply = b"200 OK\r\n"
        code = self.ftp.parse_ftp_reply(reply)
        self.assertEqual(code, "200")

    def test_parse_invalid_reply_length(self):
        """Test parsing an invalid FTP reply due to length."""
        reply = b"20"
        with self.assertRaises(BooFtpException) as context:
            self.ftp.parse_ftp_reply(reply)
        self.assertEqual(
            str(context.exception),
            "Invalid FTP reply: must be 3 digits and a space, no non-ASCII",
        )

    def test_parse_invalid_reply_non_ascii(self):
        """Test parsing an invalid FTP reply with non-ASCII characters."""
        reply = b"\xff\xff\xff "
        with self.assertRaises(BooFtpException) as context:
            self.ftp.parse_ftp_reply(reply)
        self.assertEqual(
            str(context.exception),
            "Invalid FTP reply: must be 3 digits and a space, no non-ASCII",
        )

    def test_parse_invalid_reply_format(self):
        """Test parsing an invalid FTP reply due to format."""
        reply = b"999 Not a valid code"
        with self.assertRaises(BooFtpException) as context:
            self.ftp.parse_ftp_reply(reply)
        self.assertEqual(
            str(context.exception),
            "Invalid FTP reply; must be a 3-digit sequence followed by a space",
        )


if __name__ == "__main__":
    unittest.main()
