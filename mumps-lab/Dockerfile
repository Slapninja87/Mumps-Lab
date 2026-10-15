FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends fis-gtm python3 python3-pytest \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home lab \
    && mkdir /lab \
    && chown lab:lab /lab

WORKDIR /lab
COPY --chown=lab:lab . .
USER lab

CMD ["python3", "-m", "pytest", "-v"]
