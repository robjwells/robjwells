from pathlib import Path
from typing import Set

import requests
from bs4 import BeautifulSoup, Comment

OUTPUT_FILENAME: str = "filtered.xml"


def fetch_rss_feed() -> BeautifulSoup:
    r = requests.get("https://www.dailymaverick.co.za/dmrss/")
    return BeautifulSoup(r.content, "lxml-xml")


def remove_non_declassified_items(soup: BeautifulSoup) -> None:
    """Mutates `soup`."""
    for item in soup.find_all("item"):
        if "declassified" not in item.find("category").text.lower():
            item.decompose()


def replace_rss_link_with_mine(soup: BeautifulSoup, *, filename: str = OUTPUT_FILENAME) -> None:
    """Mutates `soup`."""
    url = f"https://robjwells.github.io/robjwells/declassified-uk-rss/{filename}"
    soup.find("channel").find("link")["href"] = url


def remove_comments(soup: BeautifulSoup) -> None:
    """Mutates `soup`."""
    comments = soup.find_all(text=lambda text: isinstance(text, Comment))
    for comment in comments:
        _ = comment.extract()


def prepare_soup() -> BeautifulSoup:
    soup = fetch_rss_feed()
    remove_non_declassified_items(soup)
    replace_rss_link_with_mine(soup)
    remove_comments(soup)
    return soup


def contains_items(soup: BeautifulSoup) -> bool:
    return bool(soup.find_all("item"))


def remove_extra_line_breaks(xml: str) -> str:
    return "\n".join([line for line in xml.splitlines() if line])


def filter_out_uninteresting_xml_lines(xml: str) -> Set[str]:
    return {
        line
        for line in xml.splitlines()
        if line
        if (not line.startswith("<pubDate>") and not line.startswith("<lastBuildDate>"))
    }


def more_than_date_has_changed(
    xml: str, *, output_filename: str = OUTPUT_FILENAME
) -> bool:
    out = Path(output_filename)
    if not out.exists():
        return True
    previous_set = filter_out_uninteresting_xml_lines(out.read_text())
    current_set = filter_out_uninteresting_xml_lines(xml)
    return bool(current_set - previous_set)


def main(*, output_filename: str = OUTPUT_FILENAME) -> None:
    soup = prepare_soup()
    xml = remove_extra_line_breaks(str(soup))

    if contains_items(soup) and more_than_date_has_changed(xml):
        Path(output_filename).write_text(xml)


if __name__ == "__main__":
    main()
