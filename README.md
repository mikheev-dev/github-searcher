# Github Searcher

The repository provides a ready-to-go service to search the most popular public repositories on Github. The rank of each repository is determined based on its current number of stars.

The service is able to provide:
1. A list of the most popular repositories
2. The top 10 popular repositories.
3. The top 50 popular repositories.
4. The top 100 popular repositories.

Following search parameters are available:
1. `created_from` - return only repositories created from a given date onwards
2. `language` - return only repositories written in a specific language


## Decisions for scalability and performance
### Pagination
Pagination (page numbering) has been added to optimize search results, as well as to ensure scalability and increase performance.

`page_id` is a parameter for specifying the page number.

- If `page_id` is not specified, then only the first page will be returned
- If `page_id` exceeds the number of all existing pages, then an empty list will be returned


### Caching
The list of the most popular repositories are quite constant. Therefore, there is no need to get the repositories page directly from Github every request.

- Cache support has been added to speed up response times. But it can be disabled through the ENV settings (see below).

- The current implementation is cache in memory. The search arguments are used as keys for caching, and the resulting page is stored in the cache. The TTL default is 60 seconds.

- The defined client caching protocol. A client may be replaced.


### Github API Client
Maximum query optimization is required to ensure scalability. Therefore, it is necessary to use the **asyncio** power of Python.

Problems:
- The official Github API client for Python is synchronous, which doesn’t allow achieving the required performance
- Several existing asynchronous Github clients aren’t popular.

Proposed and implemented solution:
- My own async client prototype (tested) only for searching repositories.
- The defined client API Github protocol. A client may be replaced.


## Decisions for clarity and clean code
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


## Local service setup
### Build service
From the root of repositories run
```commandline
docker build -t github-searcher .
```

### Configure service
Before launching, all settings can be changed through the ENV parameters in the .env file.

* `LOG_LEVEL` - setup level of logs [`INFO`, `DEBUG`]
* `CACHE_ENABLE` - true if you'd like to use memory cache, false if not
* `GITHUB_API_TOKEN` - token for Github API. If it's not provided, Github constrains the rate limit.

### Run service
To run the service after building:
```commandline
docker run --name=<container_name> -idt -p 8000:8000 --env-file .env github-searcher
```

To play with the service API, please open 
http://127.0.0.1:8000/docs#

### Stop service
To stop the service:
```commandline
docker stop <container_name>
docekr rm <container_name>
```

## Run tests
Tests could be run **locally** from the root of the repository.

**Preparation**:
```commandline
pip install poetry
poetry install
```

**Run tests**
```commandline
poetry shell
export GITHUB_API_TOKEN="<your-github-api-token>"
pytest
```
