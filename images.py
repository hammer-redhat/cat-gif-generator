import io
from PIL import Image
from models import GifMeta


def extract_meta(url: str, data: bytes) -> GifMeta:
    img = Image.open(io.BytesIO(data))
    frames = getattr(img, "n_frames", 1)
    width, height = img.size
    size_kb = round(len(data) / 1024, 1)
    return GifMeta(url=url, width=width, height=height, frames=frames, size_kb=size_kb)
