from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .pipeline import run_cycle

app = FastAPI(title="Dev Brain API")

class RunCycleRequest(BaseModel):
    user_request: str
    target_file: str
    changed_files: Optional[List[str]] = None

class RunCycleResponse(BaseModel):
    frame_id: str
    prompt: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run-cycle", response_model=RunCycleResponse)
def run_cycle_endpoint(request: RunCycleRequest):
    try:
        frame_id, prompt = run_cycle(
            user_request=request.user_request,
            target_file=request.target_file,
            changed_files=request.changed_files,
        )
        return RunCycleResponse(frame_id=frame_id, prompt=prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
