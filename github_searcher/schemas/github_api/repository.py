from datetime import datetime
from pydantic import BaseModel, Field


class RepositoryOwnerModel(BaseModel):
    """
      Schema for GithubAPI response's repo object's owner
    """
    login: str


class GARepository(BaseModel):
    """
    Schema for GithubAPI response's repo object
    """
    id: int
    name: str
    full_name: str = Field(alias="full_name")
    owner: RepositoryOwnerModel
    description: str | None = Field(default=None)
    created_at: datetime = Field(alias="created_at")
    url: str = Field(alias="clone_url")
    stars: int = Field(alias="stargazers_count")
    watchers: int = Field(alias="watchers_count")
    language: str | None = Field(default=None)

