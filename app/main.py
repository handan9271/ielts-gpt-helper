from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
import json

# 设置 OpenAI 客户端
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# CORS 设置：允许 GitHub Pages 域名访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://handan9271.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 接收请求的数据结构
class IELTSRequest(BaseModel):
    question: str  # 可以是自定义输入
    input: str     # 中文思路

# AI 助教提示模板
PROMPT_TEMPLATE = """你是一位面向雅思6分以下考生的 AI 写作与口语助教，帮助学生将中文表达或英文表达转化为结构清晰、语言丰富、逐步提升的英文表达，并引导他们掌握提分关键表达。你的任务包括以下五步：

---

【TEEL结构英文表达（逐句输出 + 中文翻译 + 高亮表达）】
题目如下：{question}

学生中文思路如下：{input_text}

请按照以下格式逐步生成英文回答，每句英文下方附中文翻译，重要表达用**加粗**或==高亮==表示。每段不超过6行。

【词汇讲解】
挑选当前段落中学生可能不熟悉的词汇（3-5个），写出英文、中文解释、并给出例句。

【AI评分 + 中文反馈建议】
根据 IELTS 写作评分标准，为学生估算一个 Band 分，并指出优点和改进建议。

【高分参考段落（英文 + 中文 + 高亮表达）】
生成一个更高分数（+1分）的完整英文段落，与学生原始表达相同主题，逐句翻译并高亮表达。
"""

# 主接口：生成优化反馈
@app.post("/api/ielts-helper")
async def ielts_helper(data: IELTSRequest):
    prompt = PROMPT_TEMPLATE.format(question=data.question, input_text=data.input)
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": "你是一个雅思AI助教"},
            {"role": "user", "content": prompt}
        ]
    )
    return {"reply": response.choices[0].message.content}

# 保留随机题目接口（可选使用）
@app.get("/api/random-question")
async def random_question():
    question_prompt = """
你是一位雅思口语考官助理，请你从最近真实的 Part 2 题库中，随机选择一个热门且具启发性的题目，返回 JSON 格式：

英文题目字段是 "en"，中文翻译字段是 "zh"。

示例：
{
  "en": "Describe a time you received positive feedback.",
  "zh": "描述一次你收到积极反馈的经历"
}
只输出 JSON，其他内容不要输出。
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个雅思口语题库生成器"},
            {"role": "user", "content": question_prompt.strip()}
        ]
    )

    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except:
        return {
            "en": "Describe a piece of technology you use frequently.",
            "zh": "描述一个你经常使用的科技产品（备用题）"
        }
