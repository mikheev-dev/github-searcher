from aiohttp import ClientSession

import time
import logging

from github_searcher.exceptions import NotExistedLanguageException
from github_searcher.clients.github.client_protocol import GithubAPIClientProtocol
from github_searcher.clients.cache.cache_protocol import CacheProtocol
from github_searcher.schemas.github_api import GARepository
from github_searcher.services.search_args import SearchArgs


logger = logging.getLogger(__name__)


class ReposSearchingService:
    """
    Service for interacting with Github API via client, supported protocol.
    Could cache results.
    """
    _github_api_client: GithubAPIClientProtocol
    _cache: CacheProtocol | None

    def __init__(
            self,
            api_client: GithubAPIClientProtocol,
            cache: CacheProtocol | None = None,
    ):
        self._github_api_client = api_client
        self._cache = cache

    async def _get_from_cache(self, args: SearchArgs) -> list[GARepository]:
        """
        Try to get cached result
        :param args: search arguments (key)
        :return:
        """
        return await self._cache.get(str(args))

    async def _set_to_cache(self, args: SearchArgs, response: list[GARepository]):
        """
        Save results to cache
        :param args: search arguments (key)
        :param response: result to save
        :return:
        """
        return await self._cache.set(
            key=str(args),
            value=response,
            ttl=60,
        )

    @staticmethod
    def _check_language(args: SearchArgs, response: list[GARepository]) -> list[GARepository]:
        """
        In case if the language is not matched with any language in repos,
        GithubAPI returns response for request without language specification.
        The service should check it and raise exception

        :param args: arguments for searching
        :param response: response, got from GithubAPI
        :return: response
        """
        if args.lang and response and response[0].language.lower() != args.lang.lower():
            logger.debug(f"Language {args.lang} is not in the response repos.")
            raise NotExistedLanguageException()
        return response

    async def get_popular_repos(
            self,
            session: ClientSession,
            args: SearchArgs,
    ) -> list[GARepository]:
        """
        Get list of popular repos (from the first page or from the specified page from args),
        which satisfy search arguments.

        :param session:
        :param args: search arguments
        :return: list of repositories
        """
        logger.info(f"Get popular repos for args {args}")
        st_time = time.time()
        if self._cache:
            logger.info(f"Try to get result from cache for args {args}")
            repos_from_cache = await self._get_from_cache(args)
            if repos_from_cache:
                logger.info(f"Got result from cache for args {args}.")
                logger.debug(f"Exec time [response from cache] = {time.time() - st_time}")
                return repos_from_cache
            logger.info(f"Response not cached for args={args}, try to get it from GithubAPI.")

        repos = await self._github_api_client.search_repos(
            session=session,
            created_from=args.created_from,
            lang=args.lang,
            page_id=args.page_id,
        )
        if self._cache:
            logger.info(f"Save response to cache for args {args}")
            await self._set_to_cache(args, repos)

        repos = self._check_language(args, repos)

        logger.debug(f"Exec time [response from API ]= {time.time() - st_time}")
        return repos

    async def get_top_k_popular_repos(
            self,
            session: ClientSession,
            args: SearchArgs,
            k: int = 100,
    ) -> list[GARepository]:
        """
        Get K most popular repos from Github, which satisfy the searching arguments.
        If K repos don't exist, return all existed.

        :param session:
        :param args: search arguments
        :param k: number of repos to find
        :return: list of repositories
        """
        logger.info(f"Get top K popular repos, search args {args}.")
        args.page_id = 1
        repos = []

        while len(repos) < k:
            page = await self.get_popular_repos(
                session=session,
                args=args,
            )
            logger.debug(f"Page {args.page_id} contains {len(page)} repos")
            if not page:
                logger.info(f"Empty page for args {args}.")
                break

            repos.extend(page)
            logger.debug(f"Current length of collected repos for args {args} = {len(repos)}")
            args.page_id += 1

        return repos[:k]

