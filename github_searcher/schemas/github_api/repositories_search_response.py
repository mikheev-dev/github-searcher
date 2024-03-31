from github_searcher.schemas.github_api.repository import GARepository

from pydantic import BaseModel


class GARepositoriesSearchResponse(BaseModel):
    items: list[GARepository]

