from aiohttp import ClientSession
from datetime import date
from typing import Protocol

from github_searcher.schemas.github_api import GARepository


class GithubAPIClientProtocol(Protocol):
    """
    GithubAPI client protocol
    """
    async def search_repos(
            self,
            session: ClientSession,
            page_id: int | None = None,
            created_from: date | None = None,
            lang: str | None = None,
    ) -> list[GARepository]:
        """
        Method to search in github repos
        :param session: session for making request
        :param page_id: number of page which need to get
        :param created_from: data to search repos created after
        :param lang: language to search repos written with
        :return: list of repos
        """
        raise NotImplementedError
