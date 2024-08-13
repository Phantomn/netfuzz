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
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen && update-locale LANG=en_US.UTF-8 && \
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
RUN rm -rf netfuzz README.md

# Comment these lines if you won't run the tests.
ADD ./setup-dev.sh /netfuzz/
RUN ./setup-dev.sh

ADD . /netfuzz/

ARG LOW_PRIVILEGE_USER="vscode"

ENV PATH="${NETFUZZ_VENV_PATH}/bin:${PATH}"