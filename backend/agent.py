import os
import json
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv
from backend.prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT

load_dotenv()

class FinanceAgent:
    def __init__(self, provider="groq"):
        self.provider = "groq"
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def analyze_spending(self, text):
        prompt = ANALYSIS_PROMPT.format(text=text)
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)

        return {"status": "error", "message": "Invalid provider"}
