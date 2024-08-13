ARG IMAGE
FROM ${IMAGE} AS builder

WORKDIR /netfuzz

RUN sed -i 's@archive.ubuntu.com@mirror.kakao.com@g' /etc/apt/sources.list && \
    sed -i 's@security.ubuntu.com@mirror.kakao.com@g' /etc/apt/sources.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends locales vim && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

ADD poetry.lock pyproject.toml poetry.toml setup.sh /netfuzz/

RUN ./setup.sh

FROM ${IMAGE}

WORKDIR /netfuzz

COPY --from=builder /netfuzz /netfuzz

ADD . /netfuzz/

ADD ./setup-dev.sh /netfuzz/
RUN ./setup-dev.sh

ENV PATH="${NETFUZZ_VENV_PATH}/bin:${PATH}"
