import os, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "openai/gpt-4o-mini"

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

SYSTEM_PROMPT = """Bạn là chuyên gia tài chính nhưng giải thích cho người mới chơi chứng khoán F0-F2.
QUY TẮC: 1. CHỈ dùng số liệu được cung cấp. Cấm bịa. 2. Giọng GenZ, dễ hiểu. 3. Nếu có flags thì PHẢI nhắc rủi ro. 4. CẤM từ: mua, bán, khuyến nghị, nên đầu tư. 5. Luôn kết: "Cần theo dõi thêm báo cáo quý tới." 6. Output 2-3 câu."""

def build_user_prompt(d: FinancialData) -> str:
    return f"""Mã: {d.ticker} {d.quarter}
Doanh thu: {d.revenue}, Lợi nhuận: {d.net_profit}
Nợ/Tài sản: {d.debt_ratio:.2f}, Dòng tiền HĐKD: {d.ocf} tỷ, ROE: {d.roe:.1f}%
Điểm: {d.score}/100, Cờ: {', '.join(d.flags) if d.flags else 'Không'}"""

@app.post("/explain")
async def explain(data: FinancialData):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(data)}
        ],
        "temperature": 0.3, "max_tokens": 150
    }
    async with httpx.AsyncClient() as client:
        r = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
    content = r.json()["choices"][0]["message"]["content"]
    if any(w in content.lower() for w in ["mua", "bán", "khuyến nghị"]):
        content = "Công ty có điểm tốt và điểm cần lưu ý theo dữ liệu. Cần theo dõi thêm báo cáo quý tới."
    return {"explanation": content.strip()}

@app.get("/")
def health(): return {"status": "FinSnap AI OK"}