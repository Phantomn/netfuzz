# 빌드 스테이지
ARG image
FROM ${image} AS builder

ARG LOW_PRIVILEGE_USER="vscode"  # 빌드 스테이지에서 사용

WORKDIR /netfuzz

# 환경 변수 설정
ENV PIP_NO_CACHE_DIR=true
ENV NETFUZZ_VENV_PATH=/venv
ENV LANGUAGE=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV TZ=Asia/Seoul


# 패키지 소스 변경 및 필수 패키지 설치
RUN sed -i 's@archive.ubuntu.com@mirror.kakao.com@g' /etc/apt/sources.list && \
    sed -i 's@security.ubuntu.com@mirror.kakao.com@g' /etc/apt/sources.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends locales vim && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

# 의존성 파일 추가
ADD ./poetry.lock /netfuzz/
ADD ./pyproject.toml /netfuzz/
ADD ./poetry.toml /netfuzz/
ADD ./setup.sh /netfuzz/

# 의존성 설치
RUN DEBIAN_FRONTEND=noninteractive ./setup.sh

# 최종 이미지 스테이지
FROM ${image}

ARG LOW_PRIVILEGE_USER="vscode"  # 최종 이미지 스테이지에서 사용

WORKDIR /netfuzz

# 빌드 스테이지에서 필요한 파일 복사
COPY --from=builder /netfuzz /netfuzz

# 런타임에 필요한 패키지 설치 (필요 시)
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends vim && \
    rm -rf /var/lib/apt/lists/*

# 추가 소스 코드 복사
ADD . /netfuzz/

# 개발 환경 설정 스크립트 추가 및 실행
ADD ./setup-dev.sh /netfuzz/
RUN ./setup-dev.sh

# PATH 환경 변수 설정
ENV PATH="${NETFUZZ_VENV_PATH}/bin:${PATH}"
