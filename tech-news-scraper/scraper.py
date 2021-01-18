#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from email.mime.text import MIMEText
from itertools import chain
import smtplib
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


def send_email(body: str, subject: str) -> None:
    message = MIMEText(body, _charset="utf-8")
    message["subject"] = subject
    address = message["To"] = message["From"] = "rob@robjwells.com"

    mailer = smtplib.SMTP(host="smtp.fastmail.com", port=587)
    mailer.ehlo()
    mailer.starttls()
    mailer.login("robjwells@fastmail.fm", "7nur8nga2q24t5ps")
    mailer.sendmail(address, [address], message.as_string())
    mailer.quit()


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
        [f"{story.title}\n{story.url}" for story in sorted_stories]
    )
    subject = "HN & Lobsters digest"
    send_email(body=stories_str, subject=subject)


if __name__ == "__main__":
    sites_to_check = [
        Site(url="https://news.ycombinator.com", selector=".storylink"),
        Site(url="https://lobste.rs", selector="#inside .details a.u-url"),
    ]
    main(sites_to_check)
