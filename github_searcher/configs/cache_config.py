from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheConfig(BaseSettings):
    """
    Config to define cache settings.
    First of all, define is cache enable or not.
    """
    model_config = SettingsConfigDict(env_prefix='CACHE_')

    enable: bool = False
