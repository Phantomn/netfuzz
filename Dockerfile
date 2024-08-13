# This dockerfile was created for development & testing purposes, for APT-based distro.
#
# Build as:             docker build -t netfuzz .
#
# For testing use:      docker run --rm -it --cap-add=SYS_PTRACE --security-opt seccomp=unconfined netfuzz bash
#
# For development, mount the directory so the host changes are reflected into container:
#   docker run -it --cap-add=SYS_PTRACE --security-opt seccomp=unconfined -v `pwd`:/netfuzz netfuzz bash
#

ARG image=mcr.microsoft.com/devcontainers/base:jammy
FROM $image

WORKDIR /netfuzz

ENV PIP_NO_CACHE_DIR=true
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV TZ=Asia/Seoul
ENV NETFUZZ_VENV_PATH=/venv

RUN sed -i 's@archive.ubuntu.com@mirror.kakao.com@g' /etc/apt/sources.list
RUN sed -i 's@security.ubuntu.com@mirror.kakao.com@g' /etc/apt/sources.list

# Combine commands to reduce layers
RUN apt-get update -y && apt-get install -y --no-install-recommends locales vim && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone \
    localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 \
    locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 \
    rm -rf /var/lib/apt/lists/*

# Add necessary files
ADD ./setup.sh /netfuzz/
ADD ./poetry.lock /netfuzz/
ADD ./pyproject.toml /netfuzz/
ADD ./poetry.toml /netfuzz/

# pyproject.toml requires these files, pip install would fail
RUN touch README.md && mkdir netfuzz && touch netfuzz/empty.py

RUN DEBIAN_FRONTEND=noninteractive ./setup.sh

# Cleanup dummy files
RUN rm README.md && rm -rf netfuzz

# Comment these lines if you won't run the tests.
ADD ./setup-dev.sh /netfuzz/
RUN ./setup-dev.sh

ADD . /netfuzz/

ARG LOW_PRIVILEGE_USER="vscode"
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="~/.local/bin:${PATH}"

ENV PATH="${NETFUZZ_VENV_PATH}/bin:${PATH}"