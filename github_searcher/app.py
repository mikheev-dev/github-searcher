from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import logging

from github_searcher.api.v0.repos import api_v0_router
from github_searcher.configs.logger_config import LogConfig
from github_searcher.exceptions import (
    GithubApiRateLimitException,
    NotExistedLanguageException,
    SearchMaxResultsException,
)

log_config = LogConfig()

logging.basicConfig(
    level=log_config.level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


description = """
Service for searching popular repositories on Github.
"""


app = FastAPI(
    title="Github Searcher",
    description=description,
    summary="Web-service to search repos",
    version="0.0.1",
    contact={
        "name": "Pavel Mikheev",
        "url": "https://github.com/mikheev-dev",
        "email": "mikheevpav@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

app.include_router(
    router=api_v0_router,
    prefix="/api/v0",
)


@app.exception_handler(GithubApiRateLimitException)
async def unicorn_exception_handler(request: Request, exc: GithubApiRateLimitException):
    return JSONResponse(
        status_code=429,
        content={"message": f"Github API rate limit exceeded. Please, wait before next request or "
                            f"provide Github token and restart the server."},
    )


@app.exception_handler(SearchMaxResultsException)
async def unicorn_exception_handler(request: Request, exc: SearchMaxResultsException):
    """

    """
    return JSONResponse(
        status_code=200,
        content=[],
    )


@app.exception_handler(NotExistedLanguageException)
async def unicorn_exception_handler(request: Request, exc: NotExistedLanguageException):
    return JSONResponse(
        status_code=200,
        content=[],
    )
