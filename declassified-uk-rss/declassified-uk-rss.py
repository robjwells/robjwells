#!/usr/local/bin/python3

import requests
from bs4 import BeautifulSoup

r = requests.get("https://www.dailymaverick.co.za/dmrss/")
s = BeautifulSoup(r.content, "lxml-xml")

for item in s.find_all("item"):
    if "declassified" not in item.find("category").text.lower():
        item.decompose()

with open("filtered.xml", "wb") as out:
    out.write(s.encode("utf-8"))
