const API_BASE =
  "https://你的Render地址.onrender.com";


// =========================
// 加载校园资讯
// =========================
async function loadNews() {

  const response = await fetch(
    `${API_BASE}/api/news`
  );

  const data = await response.json();

  const newsList =
    document.getElementById("news-list");

  newsList.innerHTML = "";

  data.forEach(item => {

    newsList.innerHTML += `

      <div class="news-card">

        <h3>${item.title}</h3>

        <p>${item.summary}</p>

        <a href="${item.url}" target="_blank">
          查看原文
        </a>

      </div>

    `;
  });
}


// =========================
// URL分析
// =========================
async function analyzeUrl() {

  const url =
    document.getElementById("url-input").value;

  const result =
    document.getElementById("url-result");

  result.innerHTML = "分析中...";

  const response = await fetch(
    `${API_BASE}/api/summarize`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({ url })
    }
  );

  const data = await response.json();

  let html = `

    <h3>${data.title}</h3>

    <p>${data.summary}</p>

    <h4>🔗 页面链接</h4>
  `;

  data.links.forEach(link => {

    html += `
      <p>
        <a href="${link.url}" target="_blank">
          ${link.text || link.url}
        </a>
      </p>
    `;
  });

  html += `
    <h4>📎 附件</h4>
  `;

  data.attachments.forEach(file => {

    html += `
      <p>
        <a href="${file}" target="_blank">
          ${file}
        </a>
      </p>
    `;
  });

  result.innerHTML = html;
}


// =========================
// AI聊天
// =========================
let messages = [

  {
    role: "system",
    content: "你是AI助手"
  }

];


async function sendMessage() {

  const input =
    document.getElementById("chat-input");

  const text = input.value;

  if (!text) return;

  messages.push({
    role: "user",
    content: text
  });

  const chatBox =
    document.getElementById("chat-box");

  chatBox.innerHTML += `
    <div class="user-msg">
      ${text}
    </div>
  `;

  input.value = "";

  const response = await fetch(
    `${API_BASE}/api/chat`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        messages
      })
    }
  );

  const data = await response.json();

  messages.push({
    role: "assistant",
    content: data.reply
  });

  chatBox.innerHTML += `
    <div class="ai-msg">
      ${data.reply}
    </div>
  `;
}


loadNews();
