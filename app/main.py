from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
import json

# 创建 OpenAI 客户端（确保环境变量中有 OPENAI_API_KEY）
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# 配置 CORS：允许来自 GitHub Pages 的访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://handan9271.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型：接收用户题目 + 中文思路
class IELTSRequest(BaseModel):
    question: str
    input: str

# AI Prompt 模板：输出包括结构优化、词汇讲解、评分建议等
PROMPT_TEMPLATE = """你是一位面向雅思6分以下考生的 AI 写作与口语助教，帮助学生将中文思路转化为结构清晰、语言丰富、逐步提升的英文表达，并引导他们掌握提分关键表达。你的任务包括以下五步：

---

【TEEL结构英文表达（逐句输出 + 中文翻译 + 高亮表达）】
学生题目如下：{question}
学生中文思路如下：{input_text}

请按照以下格式逐步生成英文回答，每句英文下方附中文翻译，重要表达用**加粗**或==高亮==表示。每段不超过6行。

【词汇讲解】
挑选当前段落中学生可能不熟悉的词汇（3-5个），写出英文、中文解释、并给出例句。

【AI评分 + 中文反馈建议】
根据 IELTS 写作评分标准，为学生估算一个 Band 分，并指出优点和改进建议。

【高分参考段落（英文 + 中文 + 高亮表达）】
生成一个更高分数（+1分）的完整英文段落，与学生原始表达相同主题，逐句翻译并高亮表达。
"""

@app.post("/api/ielts-helper")
async def ielts_helper(data: IELTSRequest):
    prompt = PROMPT_TEMPLATE.format(input_text=data.input, question=data.question)
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": "你是一个雅思AI助教"},
            {"role": "user", "content": prompt}
        ]
    )
    return {"reply": response.choices[0].message.content}
