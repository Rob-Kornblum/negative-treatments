from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from extract import extract_negative_treatments

app = FastAPI()

class CaseRequest(BaseModel):
    case_id: str

@app.post("/negative-treatments")
def get_negative_treatments(request: CaseRequest):
    try:
        result = extract_negative_treatments(request.case_id)
        return {"negative_treatments": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))