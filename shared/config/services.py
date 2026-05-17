from shared.config.base import BaseConfig


class ServiceConfig(BaseConfig):

    APP_ENV: str
    DEBUG: bool

    DJANGO_SECRET_KEY: str