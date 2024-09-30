FROM mcr.microsoft.com/devcontainers/base:jammy

WORKDIR /netfuzz

ENV TZ=Asia/Seoul \
    LANGUAGE=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PIP_NO_CACHE_DIR=true \
    DEBIAN_FRONTEND=noninteractive \
    NETFUZZ_VENV_PATH=/venv

RUN sed -i 's@archive.ubuntu.com@mirror.kakao.com@g' /etc/apt/sources.list && \
    sed -i 's@security.ubuntu.com@mirror.kakao.com@g' /etc/apt/sources.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
    locales vim curl build-essential libc6-dev shfmt \
    python3.10 python3-dev python3-venv python3-setuptools python-is-python3 && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

ADD ./poetry.lock ./pyproject.toml ./poetry.toml /netfuzz/
RUN touch README.md && mkdir netfuzz && touch netfuzz/empty.py && mkdir /venv

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="$HOME/.local/bin:$PATH" && \
    python3 -m venv ${NETFUZZ_VENV_PATH} && \
    . ${NETFUZZ_VENV_PATH}/bin/activate && \
    poetry install && rm -rf README.md netfuzz

ADD ./setup-dev.sh /netfuzz/
RUN ./setup-dev.sh

ADD . /netfuzz/

ARG LOW_PRIVILEGE_USER=vscode
ENV PATH="${NETFUZZ_VENV_PATH}/bin:${PATH}"