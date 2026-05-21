import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import json
import time


BASE_URL = "http://i.whut.edu.cn/xxtg/"


headers = {
    "User-Agent": "Mozilla/5.0"
}


notice_list = []

seen = set()


# ====================================
# 遍历29页
# ====================================
for page in range(29):

    try:

        # 首页
        if page == 0:

            page_url = BASE_URL

        else:

            page_url = (
                BASE_URL
                +
                f"index_{page}.shtml"
            )

        print("正在抓取：", page_url)

        response = requests.get(

            page_url,

            headers=headers,

            timeout=15
        )

        response.encoding = (
            response.apparent_encoding
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        links = soup.find_all("a")

        for item in links:

            title = item.get_text(
                strip=True
            )

            href = item.get("href")

            if not title:
                continue

            if not href:
                continue

            # 过滤过短标题
            if len(title) < 6:
                continue

            full_url = urljoin(
                page_url,
                href
            )

            # 去重
            if full_url in seen:
                continue

            seen.add(full_url)

            # 只保留文章页
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

                "summary":
                    "武汉理工大学校内公告",

                "url": full_url
            })

        # 防止请求过快
        time.sleep(1)

    except Exception as e:

        print("抓取失败：", e)


# ====================================
# 保存JSON
# ====================================
print("总共抓取：", len(notice_list))

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

print("保存完成")