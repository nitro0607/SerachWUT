import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import json


NOTICE_URL = "http://i.whut.edu.cn/xxtg/"


headers = {
    "User-Agent": "Mozilla/5.0"
}


response = requests.get(
    NOTICE_URL,
    headers=headers,
    timeout=15
)

response.encoding = response.apparent_encoding

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

notice_list = []

links = soup.find_all("a")

seen = set()

for item in links:

    title = item.get_text(strip=True)

    href = item.get("href")

    if not title:
        continue

    if not href:
        continue

    if len(title) < 6:
        continue

    full_url = urljoin(
        NOTICE_URL,
        href
    )

    if full_url in seen:
        continue

    seen.add(full_url)

    if not (
        ".html" in full_url
        or
        ".htm" in full_url
        or
        ".shtml" in full_url
    ):
        continue

    notice_list.append({

        "title": title,

        "summary": "武汉理工大学校内公告",

        "url": full_url
    })

print("抓取成功：", len(notice_list))

with open(
    "campus_notice.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        notice_list,
        f,
        ensure_ascii=False,
        indent=2
    )