#!/usr/local/bin/python3

import requests
from bs4 import BeautifulSoup, Comment

r = requests.get("https://www.dailymaverick.co.za/dmrss/")
s = BeautifulSoup(r.content, "lxml-xml")

for item in s.find_all("item"):
    if "declassified" not in item.find("category").text.lower():
        item.decompose()

url = "https://robjwells.github.io/robjwells/declassified-uk-rss/filtered.xml"
s.find("channel").find("link")["href"] = url

comments = s.find_all(text=lambda text: isinstance(text, Comment))
for comment in comments:
    _ = comment.extract()

if s.find_all("item"):
    as_string = str(s)
    fewer_breaks = "\n".join([line for line in as_string.split("\n") if line])
    print(fewer_breaks)
    with open("filtered.xml", "wb") as out:
        out.write(fewer_breaks.encode("utf-8"))
