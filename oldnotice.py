import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin


BASE_URL = "http://218.197.103.13/xytg/"


headers = {

    "User-Agent":
        "Mozilla/5.0"
}


all_notices = []


# =========================
# 读取已有数据
# =========================

try:

    with open(
        "campus_notice.json",
        "r",
        encoding="utf-8"
    ) as f:

        existing = json.load(f)

except:

    existing = []


existing_urls = {

    item["url"]

    for item in existing
}


# =========================
# 开始抓取
# =========================

for i in range(0, 796):

    if i == 0:

        page_url = BASE_URL + "index.shtml"

    else:

        page_url = (
            BASE_URL +
            f"index_{i}.shtml"
        )

    print("正在抓取：", page_url)

    try:

        response = requests.get(

            page_url,

            headers=headers,

            timeout=15
        )

        response.encoding = "utf-8"

        soup = BeautifulSoup(

            response.text,

            "html.parser"
        )

        links = soup.find_all("a")

        for a in links:

            href = a.get("href")

            title = a.get_text(strip=True)

            if not href:
                continue

            if not title:
                continue

            # 过滤无意义链接
            if len(title) < 4:
                continue

            full_url = urljoin(
                page_url,
                href
            )

            if full_url in existing_urls:
                continue

            notice = {

                "title": title,

                "url": full_url,

                "summary": "",

                "time": ""
            }

            all_notices.append(notice)

            existing_urls.add(full_url)

        time.sleep(0.3)

    except Exception as e:

        print("抓取失败：", e)


# =========================
# 合并
# =========================

final_data = existing + all_notices


# =========================
# 保存
# =========================

with open(
    "campus_notice.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(

        final_data,

        f,

        ensure_ascii=False,

        indent=2
    )

print("历史公告导入完成")
print("新增数量：", len(all_notices))