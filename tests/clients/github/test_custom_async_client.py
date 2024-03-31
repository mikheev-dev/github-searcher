from aiohttp.client import ClientSession, ClientResponse
from datetime import date, timedelta
from unittest.mock import patch

import pytz
import pytest

from github_searcher.clients.github.custom_async_client import CustomAsyncGithubAPIClient
from github_searcher.configs.github_api_config import GithubAPIConfig
from github_searcher.exceptions import GithubApiRateLimitException

from tests.utils import (
    check_order,
    check_created_from,
    check_language,
)

utc = pytz.UTC


class TestCustomAsyncGithubAPIClient:
    _client = CustomAsyncGithubAPIClient(
        token=GithubAPIConfig().token,
    )

    @pytest.mark.asyncio
    async def test_search_default(self):
        async with ClientSession() as session:
            result = await self._client.search_repos(
                session=session,
            )
            check_order(result)

    @pytest.mark.asyncio
    @patch.object(ClientResponse, "json")
    async def test_rate_limit(self, mocked_json):
        async def json(*args, **kwargs) -> dict:
            return {
                "message": "API rate limit exceeded"
            }

        mocked_json.side_effect = json
        async with ClientSession() as session:
            with pytest.raises(GithubApiRateLimitException) as e:
                await self._client.search_repos(
                    session=session,
                )

    @pytest.mark.asyncio
    async def test_search_page(self):
        async with ClientSession() as session:
            result_page_0 = await self._client.search_repos(
                session=session,
            )
            result_page10 = await self._client.search_repos(
                session=session,
                page_id=10,
            )
            check_order(result_page_0)
            check_order(result_page10)
            assert result_page_0 != result_page10

    @pytest.mark.asyncio
    async def test_search_created_from(self):
        created_from = date.today() - timedelta(days=10)
        async with ClientSession() as session:
            result = await self._client.search_repos(
                session=session,
                created_from=created_from,
            )
            check_order(result)
            check_created_from(
                created_from=created_from,
                response=result,
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lang", ["python", "c"])
    async def test_search_language_filter(self, lang):
        async with ClientSession() as session:
            result = await self._client.search_repos(
                session=session,
                lang=lang,
            )
            check_order(result)
            check_language(
                lang=lang,
                response=result,
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lang", ["python", "go"])
    async def test_search_combination_filters(self, lang):
        created_from = date.today() - timedelta(days=10)
        async with ClientSession() as session:
            result_page_0 = await self._client.search_repos(
                session=session,
                lang=lang,
                created_from=created_from,
                page_id=0,
            )
            check_order(result_page_0)
            check_created_from(created_from=created_from, response=result_page_0)
            check_language(lang=lang, response=result_page_0)

            result_page_10 = await self._client.search_repos(
                session=session,
                lang=lang,
                created_from=created_from,
                page_id=10,
            )
            check_order(result_page_10)
            check_created_from(created_from=created_from, response=result_page_10)
            check_language(lang=lang, response=result_page_10)

            assert result_page_10 != result_page_0




