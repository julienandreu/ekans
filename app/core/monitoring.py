import sentry_sdk

from .config import settings


def init() -> None:
    if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
        sentry_sdk.init(
            dsn=str(settings.SENTRY_DSN),
            traces_sample_rate=float(settings.SENTRY_TRACE_SAMPLING),
            profiles_sample_rate=float(settings.SENTRY_PROFILES_SAMPLING),
        )
