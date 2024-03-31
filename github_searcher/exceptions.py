class GithubApiRateLimitException(Exception):
    message = "Github API rate limit exceeded, please provide auth token."


class NotExistedLanguageException(Exception):
    message = "No repos for language found in Github"


class SearchMaxResultsException(Exception):
    message = "Only the first 1000 search results are available"

