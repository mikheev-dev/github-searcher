# Github Searcher

This repository provides a simple service to search the most popular public repositories on Github (based on stars):

1. Get a list of the most popular repositories.
2. Get the top 10 popular repositories.
3. Get the top 50 popular repositories.
4. Get the top 100 popular repositories.

The service provides the ability to specify some search parameters:
1. `language` - return only repositories written in this language
2. `created from` - return only repositories, created after or on this date

## Decisions note
### Pagination
The search result for popular repositories on Github could be huge. To optimize performance and scalability, pagination 
was added for searching. The page number could be specified using the page_id parameter. If it's not specified, 
only the first page with repositories will be returned. An empty list will be returned for a page id that exceeds 
the amount of pages.

### Caching
The most popular repositories don't change often, so there is no need to get the page with repos from Github for every 
request. For performance, cache support was added. Memory cache is used in the current implementation. 
Search arguments could be used as keys for caching, and the received page is saved to cache. By default, TTL is 60 seconds. 
But the cache could be disabled using ENV settings (see below). A protocol for caching client is defined so the client could be replaced.

### Github API Client
There is an official Github API client for Python, but it's synchronous. To achieve scalability, I prefer to use the asyncio power of Python. 
There are several async Github clients for Python, but their popularity isn't great. 
So, I decided to prototype quickly my own async client only for searching in repositories. 
A protocol for the Github API client is defined so the client could be replaced.

### Code structure
The code structure (main folders) is presented below. 
```commandline
├── github_searcher  [main directory for application]
│   ├── api    [handlers and routers]
│   │   └── v0  [... first versiom]
│   ├── app.py [application]
│   ├── clients
│   │   ├── cache
│   │   └── github
│   ├── configs [configs from ENV vars]
│   ├── deps.py 
│   ├── exceptions.py
│   ├── schemas [pydantic models]
│   │   └── github_api [..for github api]
│   └── services [production logic]
└── tests 
```


## Build service
From the root of repositories run
```commandline
docker build -t github-searcher .
```

## Configure service
Configure Service
You could change some settings before running, changing ENV parameters in the .env file.

* `LOG_LEVEL` - setup level of logs [`INFO`, `DEBUG`]
* `CACHE_ENABLE` - true if you'd like to use memory cache, false if not
* `GITHUB_API_TOKEN` - token for Github API. If it's not provided, Github constrains the rate limit.

## Run service
To run the service after building:
```commandline
docker run --name=<container_name> -idt -p 8000:8000 --env-file .env github-searcher
```

To test service API, please open 
http://127.0.0.1:8000/docs#

## Stop service
To stop the service:
```commandline
docker stop <container_name>
docekr rm <container_name>
```

## Run tests
It's not possible to run tests in Docker, but it could be done **locally** from the root of repository.

**Preparation**:
```commandline
pip install poetry
poetry install
```

**Run tests**
```commandline
poetry run pytest
```
