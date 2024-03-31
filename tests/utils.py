from datetime import date

from github_searcher.schemas.github_api.repository import GARepository


def check_order(
        response: list[GARepository],
):
    ordered = sorted(response, key=lambda r: -r.stars)
    assert ordered == response, "Response should be ordered by stars"


def check_sorted_pages(
        first_page: list[GARepository],
        second_page: list[GARepository],
):
    check_order(first_page)
    check_order(second_page)
    assert first_page[-1].stars >= second_page[0].stars, "Repos are ordered desc by start through pages"


def check_created_from(
        created_from: date,
        response: list[GARepository],
):
    for r in response:
        assert r.created_at.date() >= created_from, \
            f"All created dates in repos should be greater than {created_from} value"


def check_language(
        lang: str,
        response: list[GARepository],
):
    lang = lang.lower()
    for r in response:
        assert r.language.lower() == lang, f"All repos should be with language {lang}"

