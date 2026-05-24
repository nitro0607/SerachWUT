import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import json
import time
import os


BASE_URL = "http://i.whut.edu.cn/xxtg/"


headers = {
    "User-Agent": "Mozilla/5.0"
}


# ====================================
# 读取已有JSON
# ====================================
old_data = []

if os.path.exists(
    "campus_notice.json"
):

    try:

        with open(

            "campus_notice.json",

            "r",

            encoding="utf-8"

        ) as f:

            old_data = json.load(f)

    except:

        old_data = []


# ====================================
# 已有URL集合
# ====================================
seen = set()

for item in old_data:

    url = item.get("url")

    if url:

        seen.add(url)


# ====================================
# 新公告列表
# ====================================
new_notice_list = []


# ====================================
# 只遍历前10页
# ====================================
for page in range(10):

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

            # ====================================
            # 过滤标题过短
            # ====================================
            if len(title) < 6:
                continue

            full_url = urljoin(
                page_url,
                href
            )

            # ====================================
            # 只保留正文页
            # ====================================
            if not (

                ".html" in full_url
                or
                ".htm" in full_url
                or
                ".shtml" in full_url
            ):
                continue

            # ====================================
            # 必须包含正文日期
            # 例如：
            # t20260522_xxx.shtml
            # ====================================
            if "/t20" not in full_url:
                continue

            # ====================================
            # 去重
            # ====================================
            if full_url in seen:
                continue

            seen.add(full_url)

            # ====================================
            # 新公告
            # ====================================
            new_notice_list.append({

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
# 新公告插入前面
# ====================================
final_list = (
    new_notice_list
    +
    old_data
)


# ====================================
# 最终去重
# 防止历史重复
# ====================================
unique = []

final_seen = set()

for item in final_list:

    url = item.get("url")

    if not url:
        continue

    if url in final_seen:
        continue

    final_seen.add(url)

    unique.append(item)


# ====================================
# 保存JSON
# ====================================
print("新增公告：", len(new_notice_list))

print("最终总数：", len(unique))

with open(

    "campus_notice.json",

    "w",

    encoding="utf-8"

) as f:

    json.dump(

        unique,

        f,

        ensure_ascii=False,

        indent=2
    )

print("保存完成")
