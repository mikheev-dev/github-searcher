from aiocache import Cache
from aiohttp import ClientSession
from fastapi import Depends
from typing import Annotated

from github_searcher.clients.github.client_protocol import GithubAPIClientProtocol
from github_searcher.clients.cache.cache_protocol import CacheProtocol
from github_searcher.clients.github.custom_async_client import CustomAsyncGithubAPIClient
from github_searcher.configs.github_api_config import GithubAPIConfig
from github_searcher.configs.cache_config import CacheConfig
from github_searcher.services.repos_searching import ReposSearchingService


# TODO reformat with dependency injector
# TODO choose cache backend based on configs
cache = Cache() if CacheConfig().enable else None
github_api_client = CustomAsyncGithubAPIClient(
    token=GithubAPIConfig().token,
)
repos_searching_service = ReposSearchingService(
    api_client=github_api_client,
    cache=cache,
)


def get_cache() -> CacheProtocol:
    return cache


def get_github_api_client() -> GithubAPIClientProtocol:
    return github_api_client


async def get_client_session() -> ClientSession:
    async with ClientSession() as session:
        yield session


def get_repos_searching_service() -> ReposSearchingService:
    return repos_searching_service

