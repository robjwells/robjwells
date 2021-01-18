#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import List, Set

import bs4  # type: ignore
import requests


@dataclass(frozen=True, eq=False)
class Story:
    """Story object where only the URL matters."""

    url: str
    title: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Story):
            return NotImplemented
        return self.url == other.url

    def __hash__(self) -> int:
        return hash(self.url)


@dataclass(frozen=True)
class Site:
    url: str
    selector: str


def fetch_stories(site: Site) -> Set[Story]:
    response = requests.get(site.url)
    soup = bs4.BeautifulSoup(response.content, features="html.parser")
    return {
        Story(url=el["href"], title=el.text.strip())
        for el in soup.select(site.selector)
    }


def main(sites: List[Site]) -> None:
    all_stories = chain.from_iterable(fetch_stories(site) for site in sites)
    # Keep unique stories that are external links
    filtered_stories = {
        story
        for story in all_stories
        if story.url.startswith("http")  # HN internal links
        if not story.url.startswith("https://lobste.rs")  # Lobsters internal links
    }
    # 'Shuffle' stories by sorting by URL
    sorted_stories = sorted(filtered_stories, key=lambda story: story.url)
    stories_str = "\n\n".join(
        [f"- {story.title}\n{story.url}" for story in sorted_stories]
    )
    with open("tech-news-summary.md", "w") as output_file:
        output_file.write(stories_str)


if __name__ == "__main__":
    sites_to_check = [
        Site(url="https://news.ycombinator.com", selector=".storylink"),
        Site(url="https://lobste.rs", selector="#inside .details a.u-url"),
    ]
    main(sites_to_check)
