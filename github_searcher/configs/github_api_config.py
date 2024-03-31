from pydantic_settings import BaseSettings, SettingsConfigDict


class GithubAPIConfig(BaseSettings):
    """
    Config fot GithibAPI.
    Provided GithubAPI token from env variable
    """
    model_config = SettingsConfigDict(env_prefix='GITHUB_API_')

    token: str = ""
