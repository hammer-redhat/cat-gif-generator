FROM registry.access.redhat.com/ubi9/python-312

ARG NEXUS_USER
ARG NEXUS_PASS
ARG NEXUS_PYPI_URL

ENV PIP_DEFAULT_TIMEOUT=120

WORKDIR /app

USER root
RUN dnf install -y rust cargo openssl-devel python3-devel gcc && dnf clean all
USER 1001

COPY requirements.txt .
RUN pip install --no-cache-dir \
    --index-url "https://${NEXUS_USER}:${NEXUS_PASS}@${NEXUS_PYPI_URL}/simple/" \
    --trusted-host "$(echo ${NEXUS_PYPI_URL} | cut -d'/' -f1)" \
    --timeout 120 \
    -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python3", "app.py"]
