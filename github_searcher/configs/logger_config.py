from pydantic_settings import BaseSettings, SettingsConfigDict


class LogConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='LOG_')

    level: str = "INFO"
