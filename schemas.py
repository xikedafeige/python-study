# schemas.py
from pydantic import BaseModel
from typing import List, Dict

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []