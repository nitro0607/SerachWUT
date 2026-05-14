from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
CORS(app)

# 首页
@app.route("/")
def index():
    return render_template("index.html")


# =========================
# 🤖 AI总结
# =========================
def ai_summary_stream(text):
    try:
        api_key = os.environ.get("KIMI_API_KEY")

        if not api_key:
            yield "❌ 未配置 KIMI_API_KEY"
            return

        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "moonshot-v1-auto",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的信息整理助手"
                    },
                    {
                        "role": "user",
                        "content": f"""
请对以下网页内容进行总结：

要求：
1. 使用中文
2. 提取核心信息
3. 分点输出
4. 控制在200字以内

内容：
{text[:3000]}
"""
                    }
                ]
            },
            timeout=30
        )

        data = response.json()

        if "choices" not in data:
            yield f"\n❌ AI接口异常：{data}"
            return

        full_text = data["choices"][0]["message"]["content"]

        for char in full_text:
            yield char
            time.sleep(0.01)

    except Exception as e:
        yield f"\n❌ AI总结失败：{str(e)}"


# =========================
# 🌐 提取站内链接
# =========================
def extract_links(soup, base_url):
    links = set()
    base_domain = urlparse(base_url).netloc

    for a in soup.find_all("a", href=True):
        href = a["href"]

        # 跳过无效链接
        if href.startswith("#") or href.startswith("javascript"):
            continue

        full_url = urljoin(base_url, href)

        # 只保留同站链接
        if urlparse(full_url).netloc == base_domain:
            links.add(full_url)

    return list(links)


# =========================
# 📎 提取附件
# =========================
def extract_attachments(soup, base_url):
    attachments = set()

    file_exts = [
        ".pdf", ".doc", ".docx",
        ".xls", ".xlsx",
        ".ppt", ".pptx",
        ".zip", ".rar",
        ".txt", ".csv"
    ]

    # a标签
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if any(ext in href.lower() for ext in file_exts):
            attachments.add(urljoin(base_url, href))

    # img标签
    for img in soup.find_all("img", src=True):
        attachments.add(urljoin(base_url, img["src"]))

    # iframe/embed
    for tag in soup.find_all(["iframe", "embed"]):
        if tag.get("src"):
            attachments.add(urljoin(base_url, tag["src"]))

    return list(attachments)


# =========================
# 🌐 网页总结接口
# =========================
@app.route("/api/summarize", methods=["POST", "OPTIONS"])
def summarize():

    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "未提供URL"})

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # 标题
        title = soup.title.string.strip() if soup.title else "无标题"

        # 正文
        paragraphs = soup.find_all("p")
        main_text = " ".join([p.get_text() for p in paragraphs])
        main_text = " ".join(main_text.split())

        # 站内链接
        links = extract_links(soup, url)[:20]

        # 附件
        attachments = extract_attachments(soup, url)

        # 流式返回
        def generate():

            yield f"📄 标题：{title}\n\n"

            yield "🧠 AI总结：\n"

            for chunk in ai_summary_stream(main_text):
                yield chunk

            # 站内链接
            yield "\n\n🌐 页面内链接：\n"

            if links:
                for link in links:
                    yield f"- {link}\n"
            else:
                yield "未发现站内链接\n"

            # 附件
            yield "\n📎 页面附件：\n"

            if attachments:
                for file in attachments:
                    yield f"- {file}\n"
            else:
                yield "未发现附件\n"

        return Response(
            generate(),
            content_type='text/plain; charset=utf-8'
        )

    except Exception as e:
        return jsonify({"error": str(e)})


# =========================
# 💬 AI聊天
# =========================
@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():

    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json()
    messages = data.get("messages")

    if not messages:
        return jsonify({"error": "未提供消息"})

    def generate():

        try:

            api_key = os.environ.get("KIMI_API_KEY")

            response = requests.post(
                "https://api.moonshot.cn/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "moonshot-v1-auto",
                    "messages": messages
                },
                timeout=30
            )

            data = response.json()

            if "choices" not in data:
                yield "❌ AI接口异常"
                return

            full_text = data["choices"][0]["message"]["content"]

            for char in full_text:
                yield char
                time.sleep(0.01)

        except Exception as e:
            yield f"❌ 错误：{str(e)}"

    return Response(
        generate(),
        content_type='text/plain; charset=utf-8'
    )


# =========================
# CORS
# =========================
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response


if __name__ == "__main__":
    app.run(debug=True)
