import yaml
from flask import Flask, render_template, jsonify
from models import Config
from imgur import fetch_random_urls, fetch_gif_bytes
from images import extract_meta
from storage import upload_to_s3
from secrets import get_session_token

with open("config.yaml") as f:
    _raw = yaml.safe_load(f)

config = Config(**_raw)
session_token = get_session_token()

app = Flask(__name__)
app.debug = config.app.debug


@app.route("/")
def index():
    return render_template("index.html", title=config.app.title)


@app.route("/api/gifs")
def api_gifs():
    urls = fetch_random_urls(config.app.gif_count)
    results = []

    for url in urls:
        data = fetch_gif_bytes(url)
        if data is None:
            continue

        meta = extract_meta(url, data)

        if config.storage.s3_enabled:
            key = config.storage.s3_prefix + url.split("/")[-1]
            upload_to_s3(data, config.storage.s3_bucket, key)

        results.append(meta.model_dump())

    return jsonify({"gifs": results, "session": session_token})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
