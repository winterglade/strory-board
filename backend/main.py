import os

import sys
import os
from dotenv import load_dotenv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()
print("? GROQ_API_KEY loaded:", bool(os.getenv("GROQ_API_KEY")))






from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from backend.services.script_generator import generate_script
from backend.services.image_generator import generate_image_base64
from backend.schemas import ScriptResponse



app = FastAPI(title="StoryboardGen API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    idea: str
    tone: str = "нейтральный"

@app.post("/api/generate-script", response_model=ScriptResponse)
async def generate_script_endpoint(req: GenerateRequest):
    try:
        return generate_script(req.idea, req.tone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "groq_key_set": bool(os.getenv("GROQ_API_KEY")),
        "hf_token_set": bool(os.getenv("HF_TOKEN"))
    }

