from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from extract import fetch_case_html, extract_opinion_text, extract_negative_treatments

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class CaseRequest(BaseModel):
    case_id: str

@app.post("/negative-treatments")
def get_negative_treatments(request: CaseRequest):
    try:
        result = extract_negative_treatments(request.case_id, client)
        return {"negative_treatments": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))