FROM registry.access.redhat.com/ubi9/python-312

ENV PIP_DEFAULT_TIMEOUT=120

WORKDIR /app

USER root
RUN dnf install -y rust cargo openssl-devel python3-devel gcc && dnf clean all
USER 1001

COPY requirements.txt .
COPY requirements-cryptography.txt .
RUN pip install --no-cache-dir \
    --index-url "https://pypi.org/simple" \
    --require-hashes \
    --no-deps \
    --timeout 600 \
    -r requirements-cryptography.txt

RUN pip install --no-cache-dir \
    --index-url "https://pypi.org/simple" \
    --timeout 600 \
    -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python3", "app.py"]
