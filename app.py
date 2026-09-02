import yaml
from flask import Flask, render_template, jsonify
from models import Config
from imgur import fetch_random_urls
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
    return jsonify({"gifs": [{"url": u} for u in urls], "session": session_token})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
