from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# 首页
@app.route("/")
def index():
    return render_template("index.html")

# 👉 AI总结函数（Kimi）
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# 首页
@app.route("/")
def index():
    return render_template("index.html")


# 👉 AI总结函数（Kimi + 防报错版）
def ai_summary(text):
    try:
        api_key = os.environ.get("KIMI_API_KEY")

        if not api_key:
            return "❌ 未配置 KIMI_API_KEY"

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
1. 用简洁中文
2. 提取核心信息
3. 分点输出（最多5点）
4. 控制在200字以内

内容：
{text[:2000]}
"""
                    }
                ],
                "temperature": 0.3
            },
            timeout=20
        )

        data = response.json()
        print("Kimi返回：", data)  # 👉 调试用

        # ❗ 防止 choices 报错
        if "choices" not in data:
            return f"❌ AI接口异常：{data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ AI总结失败：{str(e)}"


# 👉 网页抓取 + AI总结接口
@app.route("/api/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "未提供URL"})

    try:
        # 👉 反爬请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # 👉 标题
        title = soup.title.string.strip() if soup.title else "无标题"

        # 👉 提取正文（优先article）
        main_text = ""

        article = soup.find("article")
        if article:
            main_text = article.get_text()
        else:
            paragraphs = soup.find_all("p")
            main_text = " ".join([p.get_text() for p in paragraphs])

        # 👉 清理文本
        main_text = " ".join(main_text.split())

        if not main_text:
            return jsonify({"error": "未能提取到网页内容"})

        # 👉 AI总结
        summary = ai_summary(main_text)

        return jsonify({
            "title": title,
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# 👉 允许预检请求（CORS补充）
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


# 本地运行
if __name__ == "__main__":
    app.run(debug=True)
def summarize():
    data = request.get_json()
    url = data.get("url")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string if soup.title else "无标题"

        paragraphs = soup.find_all("p")
        main_text = " ".join([p.get_text() for p in paragraphs])
        main_text = " ".join(main_text.split())

        summary = ai_summary(main_text)

        return jsonify({
            "title": title,
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
