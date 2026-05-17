import requests

from bs4 import BeautifulSoup

from database import save_news


# 校园网站列表
CAMPUS_SITES = [

    "https://news.whut.edu.cn/",

]


def ai_summary(text):

    if len(text) <= 200:
        return text

    return text[:200] + "..."


def crawl_page(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    return response.text


def crawl_campus_news():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for site in CAMPUS_SITES:

        try:

            html = crawl_page(site)

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

            links = soup.find_all("a")[:20]

            for item in links:

                title = item.get_text(strip=True)

                href = item.get("href")

                if not href:
                    continue

                if href.startswith("/"):
                    href = site.rstrip("/") + href

                try:

                    article_html = crawl_page(href)

                    article_soup = BeautifulSoup(
                        article_html,
                        "html.parser"
                    )

                    paragraphs = article_soup.find_all("p")

                    content = " ".join(
                        [p.get_text() for p in paragraphs]
                    )

                    content = " ".join(content.split())

                    if len(content) < 100:
                        continue

                    summary = ai_summary(content)

                    save_news(
                        title,
                        summary,
                        content,
                        href
                    )

                    print("已保存：", title)

                except Exception as e:

                    print("文章抓取失败：", str(e))

        except Exception as e:

            print("校园抓取失败：", str(e))