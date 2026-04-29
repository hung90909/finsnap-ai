import os, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class FinancialData(BaseModel):
    ticker: str
    quarter: str
    revenue: List[float]
    net_profit: List[float]
    debt_ratio: float
    ocf: float
    roe: float
    flags: List[str]
    score: int

@app.post("/explain")
async def explain(data: FinancialData):
    if not OPENROUTER_API_KEY:
        return {"explanation": "Lỗi: Chưa cấu hình OPENROUTER_API_KEY"}

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": "Bạn là chuyên gia tài chính GenZ. Tóm tắt 2-3 câu, không khuyến nghị đầu tư."},
            {"role": "user", "content": f"Mã {data.ticker} {data.quarter}. Điểm {data.score}/100. Flags: {data.flags}"}
        ],
        "temperature": 0.3, "max_tokens": 150
    }
    async with httpx.AsyncClient() as client:
        r = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
    return {"explanation": r.json()["choices"][0]["message"]["content"].strip()}

@app.get("/")
def health(): return {"status": "FinSnap AI OK"}
