from datetime import date, timedelta
from unittest.mock import patch

import asyncio
import aiocache
import pytest

from github_searcher.services.repos import ReposService
from github_searcher.services.search_args import SearchArgs
from github_searcher.exceptions import (
    GithubApiRateLimitException,
    NotExistedLanguageException,
    SearchMaxResultsException,
)


from tests.mocked_github_api_client import MockedGithubAPIClient
from tests.utils import (
    check_sorted_pages,
    check_order,
    check_created_from,
    check_language,
)


class TestReposService:
    _service = ReposService(
        api_client=MockedGithubAPIClient()
    )

    @pytest.mark.asyncio
    @patch.object(MockedGithubAPIClient, "search_repos")
    async def test_get_popular_repos_rate_limit(self, mocked_search):
        async def raise_rate_limit(*args, **kwargs):
            raise GithubApiRateLimitException()

        mocked_search.side_effect = raise_rate_limit
        with pytest.raises(GithubApiRateLimitException) as e:
            await self._service.get_popular_repos(
                session=None,
                args=SearchArgs(created_from=None, lang=None)
            )

    @pytest.mark.asyncio
    @patch.object(MockedGithubAPIClient, "search_repos")
    async def test_get_popular_repos_max_search_exceeded(self, mocked_search):
        async def raise_max_search(*args, **kwargs):
            raise SearchMaxResultsException()

        mocked_search.side_effect = raise_max_search
        with pytest.raises(SearchMaxResultsException) as e:
            await self._service.get_popular_repos(
                session=None,
                args=SearchArgs(created_from=None, lang=None)
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("created_from, lang", [
        (None, None),
        (date.today() - timedelta(days=10), None),
        (None, "go"),
        (date.today() - timedelta(days=10), "go")
    ])
    async def test_get_popular_repos(self, created_from, lang):
        page0, page2 = await asyncio.gather(
            self._service.get_popular_repos(
                session=None,
                args=SearchArgs(
                    created_from=created_from,
                    lang=lang,
                    page_id=0,
                ),
            ),
            self._service.get_popular_repos(
                session=None,
                args=SearchArgs(
                    created_from=created_from,
                    lang=lang,
                    page_id=2,
                ),
            )
        )
        check_sorted_pages(page0, page2)
        if created_from is not None:
            check_created_from(created_from, page0)
            check_created_from(created_from, page2)

        if lang is not None:
            check_language(lang, page0)
            check_language(lang, page2)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("created_from", [None, date.today() - timedelta(days=10)])
    async def test_get_popular_repos_for_not_existed_lang(self, created_from):
        bad_lang = "notexistedlang"
        with pytest.raises(NotExistedLanguageException):
            repos = await self._service.get_popular_repos(
                session=None,
                args=SearchArgs(
                    created_from=created_from,
                    lang=bad_lang,
                ),
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lang", [None, "notexisted", "go"])
    async def test_get_popular_repos_for_date_in_future(self, lang):
        created_from = date.today() + timedelta(days=1)
        repos = await self._service.get_popular_repos(
            session=None,
            args=SearchArgs(
                created_from=created_from,
                lang=lang,
            ),
        )
        assert len(repos) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("k", [0, 10, 50, 100])
    @pytest.mark.parametrize("created_from, lang", [
        (None, None),
        (date.today() - timedelta(days=10), None),
        (None, "go"),
        (date.today() - timedelta(days=10), "go")
    ])
    async def test_get_top_k_repos(self, k, created_from, lang):
        k = 100
        top_k = await self._service.get_top_k_popular_repos(
            session=None,
            k=k,
            args=SearchArgs(
                created_from=created_from,
                lang=lang,
            )
        )

        assert len(top_k) <= k, f"Length of response should be equal or less {k}"
        check_order(top_k)
        if lang:
            check_language(lang, top_k)
        if created_from:
            check_created_from(created_from, top_k)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("created_from", [None, date.today() - timedelta(days=10)])
    async def test_get_top_k_repos_for_not_existed_lang(self, created_from):
        bad_lang = "notexistedlang"
        k = 100

        with pytest.raises(NotExistedLanguageException):
            top_k = await self._service.get_top_k_popular_repos(
                session=None,
                k=k,
                args=SearchArgs(
                    created_from=created_from,
                    lang=bad_lang,
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("lang", [None, "notexisted", "go"])
    async def test_get_top_k_repos_for_date_in_future(self, lang):
        created_from = date.today() + timedelta(days=1)
        top_k = await self._service.get_top_k_popular_repos(
            session=None,
            args=SearchArgs(
                created_from=created_from,
                lang=lang,
            ),
        )
        assert len(top_k) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_cache, page_cached", (
            [False, False],
            [True, False],
            [True, True],
    ))
    @pytest.mark.parametrize("created_from, lang, ", [
        (None, None),
        (date.today() - timedelta(days=10), None),
        (None, "go"),
        (date.today() - timedelta(days=10), "go")
    ])
    @patch.object(ReposService, "_get_from_cache")
    @patch.object(ReposService, "_set_to_cache")
    async def test_use_cache(self, set_to_cache, get_from_cache, use_cache, page_cached, created_from, lang):
        service = ReposService(
            api_client=MockedGithubAPIClient(),
            cache=aiocache.Cache() if use_cache else None,
        )

        args = SearchArgs(
            created_from=created_from,
            lang=lang,
            page_id=0,
        )

        if not page_cached:
            get_from_cache.return_value = None

        page = await service.get_popular_repos(
            session=None,
            args=args,
        )

        if use_cache:
            get_from_cache.assert_called_once_with(args)
            if page_cached:
                set_to_cache.assert_not_called()
            else:
                set_to_cache.assert_called_once_with(args, page)
        else:
            get_from_cache.assert_not_called()
            set_to_cache.assert_not_called()
