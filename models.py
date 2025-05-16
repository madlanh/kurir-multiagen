from pydantic import BaseModel
from typing import Optional

class Agent(BaseModel):
    id: str
    x: int
    y: int

class RegisterRequest(BaseModel):
    id: str

class RegisterResponse(BaseModel):
    id: str
    x: int
    y: int
    message: str