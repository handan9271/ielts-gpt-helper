
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IELTSRequest(BaseModel):
    question: str
    input: str

PROMPT_TEMPLATE = """你是一位面向雅思6分以下考生的 AI 写作与口语助教，帮助学生将中文思路转化为结构清晰、语言丰富、逐步提升的英文表达，并引导他们掌握提分关键表达。你的任务包括以下五步：

---

【第1步：当前题目】
本次题目是：{question}

【第2步：TEEL结构英文表达（逐句输出 + 中文翻译 + 高亮表达）】
学生中文思路如下：{input_text}

请按照以下格式逐步生成英文回答，每句英文下方附中文翻译，重要表达用**加粗**或==高亮==表示。每段不超过6行。

【第3步：词汇讲解】
挑选当前段落中学生可能不熟悉的词汇（3-5个），写出英文、中文解释、并给出例句。

【第4步：AI评分 + 中文反馈建议】
根据 IELTS 写作评分标准，为学生估算一个 Band 分，并指出优点和改进建议。

【第5步：高分参考段落（英文 + 中文 + 高亮表达）】
生成一个更高分数（+1分）的完整英文段落，与学生原始表达相同主题，逐句翻译并高亮表达。
"""

@app.post("/api/ielts-helper")
async def ielts_helper(data: IELTSRequest):
    prompt = PROMPT_TEMPLATE.format(input_text=data.input, question=data.question)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一个雅思AI助教"},
            {"role": "user", "content": prompt}
        ]
    )
    return {"reply": response.choices[0].message.content}
