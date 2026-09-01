from pydantic import BaseModel, HttpUrl


class GifMeta(BaseModel):
    url: str
    width: int
    height: int
    frames: int
    size_kb: float


class AppConfig(BaseModel):
    title: str
    gif_count: int
    debug: bool


class StorageConfig(BaseModel):
    s3_enabled: bool
    s3_bucket: str
    s3_prefix: str


class Config(BaseModel):
    app: AppConfig
    storage: StorageConfig
