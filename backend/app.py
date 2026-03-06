from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.agent import FinanceAgent
import uvicorn

app = FastAPI(title="AI Destekli Finans Asistanı API")

class SpendingRequest(BaseModel):
    text: str
    provider: str = "gemini"

@app.get("/")
def read_root():
    return {"message": "Finans Asistanı API Hazır!"}

@app.post("/analyze")
async def analyze_text(request: SpendingRequest):
    try:
        agent = FinanceAgent(provider=request.provider)
        result = agent.analyze_spending(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
