import requests
import certifi

_HEADERS = {
    "User-Agent": "cat-gif-viewer/1.0",
}

# Cataas (Cat as a Service) returns random cat GIFs with no credentials needed.
# Each call to /cat/gif returns a unique GIF directly.
_CATAAS_BASE = "https://cataas.com"


def fetch_random_urls(count: int) -> list[str]:
    """Return `count` unique cataas GIF URLs (each with a cache-busting tag)."""
    return [f"{_CATAAS_BASE}/cat/gif?_={i}" for i in range(count)]


def fetch_gif_bytes(url: str) -> bytes | None:
    try:
        resp = requests.get(url, timeout=15, verify=certifi.where(), headers=_HEADERS)
        resp.raise_for_status()
        return resp.content
    except requests.RequestException:
        return None
