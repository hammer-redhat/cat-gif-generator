FROM registry.access.redhat.com/ubi9/python-312

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir \
    --extra-index-url https://packages.redhat.com/lightwell/public-lightwell-demo/python/validated/ \
    -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python3", "app.py"]
