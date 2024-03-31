from aiohttp import ClientSession
from datetime import date
from fastapi import APIRouter, Depends, Query
from typing import Annotated

from github_searcher.deps import (
    get_repos_service,
    get_client_session,
)
from github_searcher.schemas.github_api import GARepository
from github_searcher.services.repos import ReposService
from github_searcher.services.search_args import SearchArgs

api_v0_router = APIRouter()


@api_v0_router.get(
    "/repos/popular",
    response_model=list[GARepository],
)
async def get_repos_by_popularity(
        repos_service: Annotated[ReposService, Depends(get_repos_service)],
        session: Annotated[ClientSession, Depends(get_client_session)],
        created_from: date | None = Query(None, description="Date to filter repos created from (Optional)"),
        language: str | None = Query(None, description="Filter the language of repos (Optional)"),
        page_id: int | None = Query(None, ge=1, description="The number of page with results to receive (Optional)"),
):
    """
    Handler to get the repos list, sorted desc by number of starts.
    Because the search result could be very big, the response is paginated.
    """
    return await repos_service.get_popular_repos(
        session=session,
        args=SearchArgs(
            created_from=created_from,
            lang=language,
            page_id=page_id,
        ),
    )


@api_v0_router.get(
    "/repos/top10",
    response_model=list[GARepository],
)
async def get_top10_repos(
        repos_service: Annotated[ReposService, Depends(get_repos_service)],
        session: Annotated[ClientSession, Depends(get_client_session)],
        created_from: date | None = Query(None, description="Date to filter repos created from (Optional)"),
        language: str | None = Query(None, description="Filter the language of repos (Optional)"),
):
    """
    Handler to get top 10 repositories.
    """
    return await repos_service.get_top_k_popular_repos(
        session=session,
        k=10,
        args=SearchArgs(
            created_from=created_from,
            lang=language,
        ),
    )


@api_v0_router.get(
    "/repos/top50",
    response_model=list[GARepository],
)
async def get_top50_repos(
        repos_service: Annotated[ReposService, Depends(get_repos_service)],
        session: Annotated[ClientSession, Depends(get_client_session)],
        created_from: date | None = Query(None, description="Date to filter repos created from (Optional)"),
        language: str | None = Query(None, description="Filter the language of repos (Optional)"),
):
    """
       Handler to get top 50 repositories.
   """
    return await repos_service.get_top_k_popular_repos(
        session=session,
        args=SearchArgs(
            created_from=created_from,
            lang=language,
        ),
        k=50,
    )


@api_v0_router.get(
    "/repos/top100",
    response_model=list[GARepository],
)
async def get_top100_repos(
        repos_service: Annotated[ReposService, Depends(get_repos_service)],
        session: Annotated[ClientSession, Depends(get_client_session)],
        created_from: date | None = Query(None, description="Date to filter repos created from (Optional)"),
        language: str | None = Query(None, description="Filter the language of repos (Optional)"),
):
    """
       Handler to get top 100 repositories.
   """
    return await repos_service.get_top_k_popular_repos(
        session=session,
        args=SearchArgs(
            created_from=created_from,
            lang=language,
        ),
        k=100,
    )


