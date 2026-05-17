import requests

from bs4 import BeautifulSoup

from urllib.parse import urljoin

from database import save_news


NEWS_URL = "https://news.whut.edu.cn/"


def crawl_campus_news():

    print("开始抓取校园资讯")

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            NEWS_URL,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        # 中文编码修复
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        news_items = soup.find_all("a")

        count = 0

        for item in news_items:

            title = item.get_text(strip=True)

            href = item.get("href")

            if not title:
                continue

            if not href:
                continue

            # 标题长度过滤
            if len(title) < 10:
                continue

            # 只保留新闻正文链接
            if not (
                "/2026/" in href
                or
                "/xw/" in href
                or
                "/zhxw/" in href
            ):
                continue

            full_url = urljoin(
                NEWS_URL,
                href
            )

            print("抓到资讯：", title)

            save_news(

                title,

                "武汉理工大学校园资讯",

                full_url
            )

            count += 1

            if count >= 20:
                break

        print(f"资讯抓取完成，共{count}条")

    except Exception as e:

        print("校园资讯抓取失败：", e)
