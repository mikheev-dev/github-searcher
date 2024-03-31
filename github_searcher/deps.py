from aiocache import Cache
from aiohttp import ClientSession
from fastapi import Depends
from typing import Annotated

from github_searcher.clients.github.client_protocol import GithubAPIClientProtocol
from github_searcher.clients.cache.cache_protocol import CacheProtocol
from github_searcher.clients.github.custom_async_client import CustomAsyncGithubAPIClient
from github_searcher.configs.github_api_config import GithubAPIConfig
from github_searcher.configs.cache_config import CacheConfig
from github_searcher.services.repos import ReposService


# TODO reformat with dependency injector
# TODO choose cache backend based on configs
cache = Cache() if CacheConfig().enable else None
github_api_client = CustomAsyncGithubAPIClient(
    token=GithubAPIConfig().token,
)
repos_service = ReposService(
    api_client=github_api_client,
    cache=cache,
)


def get_cache() -> Cache:
    return cache


def get_github_api_client() -> CustomAsyncGithubAPIClient:
    return github_api_client


async def get_client_session() -> ClientSession:
    async with ClientSession() as session:
        yield session


def get_repos_service() -> ReposService:
    return repos_service

