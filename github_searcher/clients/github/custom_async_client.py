from aiohttp import ClientSession
from datetime import date

import logging

from github_searcher.clients.github.url_builder import GithubAPIUrlBuilder
from github_searcher.exceptions import (
    GithubApiRateLimitException,
    SearchMaxResultsException,
)
from github_searcher.schemas.github_api import (
    GARepository,
    GARepositoriesSearchResponse,
)


logger = logging.getLogger(__name__)


class CustomAsyncGithubAPIClient:
    """
    Custom asynchronius client
    """
    _token: str | None

    def __init__(self, token: str | None = None):
        self._token = token

    @staticmethod
    def _check_rate_limit_msg(msg: str) -> bool:
        return "rate limit exceeded" in msg.lower()

    @staticmethod
    def _check_search_result_limit(msg: str) -> bool:
        return "Only the first 1000 search results are available".lower() == msg.lower()

    @staticmethod
    def _check_response(response: dict):
        """
        Check response from GithubAPI for errors, and raise exceptions if were found.
        :param response: GithubAPI response
        :return:
        """
        if "message" in response.keys():
            msg = response["message"]
            if CustomAsyncGithubAPIClient._check_rate_limit_msg(msg):
                raise GithubApiRateLimitException()
            elif CustomAsyncGithubAPIClient._check_search_result_limit(msg):
                raise SearchMaxResultsException()

    async def search_repos(
        self,
        session: ClientSession,
        page_id: int = 0,
        created_from: date | None = None,
        lang: str | None = None,
    ) -> list[GARepository]:
        """
        Main method to search through github repos, using aiohttp to connect to API.
        If token is provided, apply for requests (increases rate limits to API)

        :param session: session for making request
        :param page_id: number of page which need to get
        :param created_from: data to search repos created after
        :param lang: language to search repos written with
        :return: list of repos
        """
        url = GithubAPIUrlBuilder.get_search_repositories_url(
            page_id=page_id,
            created_from=created_from,
            lang=lang,
        )
        headers = {
            "Authorization": f"Bearer {self._token}"
        } if self._token else {}

        logger.debug(f"CustomAsyncGithubAPIClient: GET {url}")
        api_response = await session.get(
            url=url,
            headers=headers,
        )
        response_json = await api_response.json()
        self._check_response(response_json)
        parsed_response = GARepositoriesSearchResponse(**response_json)
        return parsed_response.items

