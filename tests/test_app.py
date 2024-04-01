from datetime import date, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch

import pytest

from github_searcher.app import app
from github_searcher.deps import get_repos_searching_service
from github_searcher.exceptions import GithubApiRateLimitException
from github_searcher.schemas.github_api import GARepository
from github_searcher.services.repos_searching import ReposSearchingService

from tests.mocked_github_api_client import MockedGithubAPIClient
from tests.utils import check_language, check_order, check_created_from

repos_searching_service = ReposSearchingService(
    api_client=MockedGithubAPIClient(),
    cache=None,
)


def override_get_repos_searching_service() -> ReposSearchingService:
    return repos_searching_service


app.dependency_overrides[get_repos_searching_service] = override_get_repos_searching_service

client = TestClient(app)

POPULAR_REPOS_HANDLER = "/api/v0/repos/popular"
TOP_K_HANDLERS = [
    "/api/v0/repos/top10",
    "/api/v0/repos/top50",
    "/api/v0/repos/top100",
]

HANDLERS_WITH_COMMON_BEHAVIOUR = [POPULAR_REPOS_HANDLER] + TOP_K_HANDLERS


@pytest.mark.parametrize("invalid_page_id", [-100, -50, 0])
def test_invalid_page_id(invalid_page_id):
    response = client.get(
        url=POPULAR_REPOS_HANDLER,
        params={
            "page_id": invalid_page_id,
        }
    )
    assert response.status_code == 422


@pytest.mark.parametrize("page_id", [100, 200])
def test_over_max_page_count(page_id):
    response = client.get(
        url=POPULAR_REPOS_HANDLER,
        params={
            "page_id": page_id,
        }
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("handler", HANDLERS_WITH_COMMON_BEHAVIOUR)
def test_invalid_language(handler):
    language = "notexistedlang"

    response = client.get(
        url=handler,
        params={
            "language": language,
        }
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("handler", HANDLERS_WITH_COMMON_BEHAVIOUR)
def test_empty_for_created_from(handler):
    created_from = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(created_from)
    response = client.get(
        url=handler,
        params={
            "created_from": created_from,
        }
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("handler", HANDLERS_WITH_COMMON_BEHAVIOUR)
@patch.object(MockedGithubAPIClient, "search_repos")
def test_catch_rate_limit(mocked_search, handler):
    async def raise_rate_limit(*args, **kwargs):
        raise GithubApiRateLimitException()

    mocked_search.side_effect = raise_rate_limit

    response = client.get(
        url=handler,
    )

    assert response.status_code == 429


@pytest.mark.parametrize("handler", HANDLERS_WITH_COMMON_BEHAVIOUR)
@pytest.mark.parametrize("created_from", [None, date.today() - timedelta(days=120)])
@pytest.mark.parametrize("language", [None, "go", "python"])
def test_app_valid_requests(handler, created_from, language):
    params = {}
    if created_from:
        params["created_from"] = created_from.strftime("%Y-%m-%d")
    if language:
        params["language"] = language

    response = client.get(
        url=handler,
        params=params,
    )

    assert response.status_code == 200

    response = [
        GARepository(**r)
        for r in response.json()
    ]

    check_order(response)
    if language:
        check_language(language, response)
    if created_from:
        check_created_from(created_from, response)
