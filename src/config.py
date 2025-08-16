from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379"
    processor_default_url: str = "http://payment-processor-default:8080"
    processor_fallback_url: str = "http://payment-processor-fallback:8080"
    instance_id: str = "API-1"


settings = Settings()
