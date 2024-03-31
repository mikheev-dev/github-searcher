from aiohttp import ClientSession
from datetime import date, timedelta
from github_searcher.schemas.github_api import (
    GARepository,
)

import asyncio
import random


class MockedGithubAPIClient:
    VALID_LANGS = ["python", "go", "c", "c++"]

    PAGE_LEN = 10
    MAX_PAGE_COUNT = 50

    @staticmethod
    def gen_repo(
            stars: int,
            created_from: date | None = None,
            lang: str | None = None,
    ):
        created_from = created_from or (date.today() - timedelta(days=10))

        if lang is None or (lang and lang not in MockedGithubAPIClient.VALID_LANGS):
            lang = random.choice(MockedGithubAPIClient.VALID_LANGS)

        return dict(
            id=10,
            name="mocked_repo",
            full_name="Py Test",
            owner=dict(
                login="pytest",
            ),
            description="",
            created_at=created_from + timedelta(days=random.randint(1, 5)),
            clone_url="test.com",
            stargazers_count=stars,
            watchers_count=stars,
            language=lang,
        )

    async def search_repos(
            self,
            session: ClientSession,
            page_id: int | None = None,
            created_from: date | None = None,
            lang: str | None = None,
    ) -> list[GARepository]:
        page_id = page_id or 0
        await asyncio.sleep(0.1)

        if created_from and created_from > date.today():
            return []

        return [
            GARepository(
                **self.gen_repo(
                    stars=50 * (self.MAX_PAGE_COUNT - page_id) - 3 * idx,
                    created_from=created_from,
                    lang=lang,
                )
            )
            for idx in range(self.PAGE_LEN)
        ]
