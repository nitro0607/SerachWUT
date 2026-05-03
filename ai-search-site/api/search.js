export default async function handler(req, res) {
  try {
    const { query } = req.body;

    const response = await fetch("https://api.moonshot.cn/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.KIMI_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "moonshot-v1-8k",
        messages: [
          {
            role: "system",
            content: "你是一个有用的AI搜索助手"
          },
          {
            role: "user",
            content: query
          }
        ],
        temperature: 0.7
      })
    });

    const data = await response.json();

    if (!data.choices) {
      return res.status(500).json({
        result: "API返回异常：" + JSON.stringify(data)
      });
    }

    res.status(200).json({
      result: data.choices[0].message.content
    });

  } catch (error) {
    res.status(500).json({
      result: "服务器错误：" + error.message
    });
  }
}
