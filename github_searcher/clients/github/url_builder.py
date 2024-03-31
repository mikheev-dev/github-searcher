from datetime import date

import os


class GithubAPIUrlBuilder:
    """
    Class to build URLs for requests to GithubAPI
    """
    GITHUB_API_URL = "https://api.github.com"
    GITHUB_API_SEARCH_URL = os.path.join(
        GITHUB_API_URL,
        "search",
    )
    GITHUB_API_SEARCH_REPOSITORIES_URL = os.path.join(
        GITHUB_API_SEARCH_URL,
        "repositories",
    )

    @classmethod
    def _search_query(
        cls,
        page_id: int | None = None,
        created_from: date | None = None,
        lang: str | None = None,
    ) -> str:
        """
        Build search query in GithibAPI required format.
        :param page_id: number of page which need to get
        :param created_from: data to search repos created after
        :param lang: language to search repos written with
        :return: query
        """

        # Without filter on starts, GithubAPI produces invalid response.
        q = [
            "is:public",
            "stars:>1",
        ]
        if created_from:
            q.append(f"created:>{created_from.strftime('%Y-%m-%d')}")
        if lang:
            q.append(f"language:{lang}")

        query = [
            '+'.join(q),
            "sort=stars",
            "order=desc",
        ]

        if page_id:
            query.append(f"page={page_id}")

        return '&'.join(query)

    @classmethod
    def get_search_repositories_url(
        cls,
        page_id: int | None = None,
        created_from: date | None = None,
        lang: str | None = None,
    ) -> str:
        """
        Build URL of searching in Githib.
        :param page_id: number of page which need to get
        :param created_from: data to search repos created after
        :param lang: language to search repos written with
        :return: URL for GET request
        """
        q = cls._search_query(
            page_id=page_id,
            created_from=created_from,
            lang=lang,
        )
        return f"{cls.GITHUB_API_SEARCH_REPOSITORIES_URL}?q={q}"
