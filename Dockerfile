ARG PYTHON_VERSION=3.10
ARG OS_VARIANT=bullseye-slim

FROM python:${PYTHON_VERSION}-${OS_VARIANT}

ARG PYTHON_VERSION
ENV PYTHON_VERSION=${PYTHON_VERSION}
ARG OS_VARIANT
ENV OS_VARIANT=${OS_VARIANT}

# This is required should be supplied as a build-arg
ARG WHEEL_TO_INSTALL
RUN test -n "${WHEEL_TO_INSTALL}" || (echo "Must supply WHEEL_TO_INSTALL as build arg"; exit 1)

COPY dist/${WHEEL_TO_INSTALL} dist/${WHEEL_TO_INSTALL}

# NodeJS needs libstdc++ to be present
# https://github.com/nodejs/unofficial-builds/#builds
RUN if echo "${OS_VARIANT}" | grep -e "alpine"; then \
    apk add libstdc++; \
    fi

RUN pip install dist/${WHEEL_TO_INSTALL}

RUN python -W error -m nodejs --version
RUN python -W error -m nodejs.npm --version
RUN python -W error -m nodejs.npx --version
RUN python -W error -m nodejs.corepack --version
