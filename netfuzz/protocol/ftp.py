from __future__ import annotations

import os
from typing import Optional

from boofuzz import Block
from boofuzz import Delim
from boofuzz import Request
from boofuzz import Static
from boofuzz import String

from netfuzz.core.base import Base


class FTP(Base):
    def __init__(self, target_ip: str, target_port: int = 21) -> None:
        super().__init__("FTP", target_ip, target_port)
        self.path = "/home/user"
        self.command = [
            ("USER", "ftp"),  # 사용자 이름
            ("PASS", "ftp"),  # 비밀번호
            ("PWD", None),  # 현재 디렉토리 확인
            ("CWD", "/tmp/test"),  # 디렉토리 변경
            ("MKD", "/tmp/test2"),  # 디렉토리 생성
            ("DELE", "test.txt"),  # 파일 삭제
            ("RMD", "/tmp/test"),  # 디렉토리 삭제
            ("ABOR", None),  # 전송 중단
            ("ACCT", "user"),  # 사용자 계정 정보 제공
            ("ALLO", "1000"),  # 공간 할당
            ("APPE", "append.txt"),  # 파일 추가 모드 전송
            ("HELP", None),  # 명령어 도움말 표시
            ("LIST", None),  # 디렉토리 파일 목록 표시
            ("MODE", "S"),  # 전송 모드 설정
            ("NLST", None),  # 파일 이름 목록 반환
            ("NOOP", None),  # 아무 작업 수행 안 함
            ("PASV", None),  # 패시브 모드 전환
            ("PORT", "1234"),  # 데이터 전송 포트 설정
            ("QUIT", None),  # FTP 세션 종료
            ("REIN", None),  # 세션 재설정
            ("REST", "50"),  # 파일 전송 재시작 지점 설정
            ("RETR", "test.txt"),  # 파일 다운로드
            ("RNFR", "rename.txt"),  # 파일 이름 변경 (원본 이름)
            ("RNTO", "new_rename.txt"),  # 파일 이름 변경 (새 이름)
            ("SITE", "CHMOD 755 test.txt"),  # 사이트별 명령어 전달
            ("STAT", None),  # 서버 상태 정보
            ("STOR", "flag.txt"),  # 파일 업로드
            ("STRU", "F"),  # 파일 구조 설정
            ("TYPE", "A"),  # 전송 파일 유형 설정
        ]
        self.update_commands_with_files()

    def scan_directory_files(self) -> list[str]:
        if not os.path.isdir(self.path):
            raise ValueError(f"유효하지 않은 디렉토리 경로: {self.path}")
        return [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]

    def update_commands_with_files(self) -> None:
        files = self.scan_directory_files()
        command_dict = dict(self.command)

        command_dict.update(
            {
                "RETR": files[0] if files else "default.txt",  # 첫 번째 파일로 다운로드 테스트
                "STOR": "upload_file.txt",  # 업로드할 파일
                "RNFR": files[0] if files else "default.txt",  # 이름 변경할 원본 파일
                "RNTO": "renamed_file.txt",
            }
        )
        self.command = list(command_dict.items())

    def initialize(self) -> None:
        for cmd, arg in self.command:
            req = self.create_req(cmd, arg)
            self.session.connect(self.session.root, req)

    def create_req(self, cmd: str, arg: Optional[str] = None) -> Request:
        if arg is None:
            block = Block(name="Command", children=[String(name="command", default_value=cmd)])
        else:
            block = Block(
                "Command",
                children=(
                    String(name="command", default_value=cmd),
                    Delim(name="space", default_value=" ") if arg else None,
                    String(name="argument", default_value=arg) if arg else None,
                ),
            )

        return Request(
            name=cmd.lower(),
            children=(
                block,
                Static(name="end", default_value="\r\n"),
            ),
        )
