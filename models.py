from pydantic import BaseModel
from typing import Optional, List, Tuple

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

class MoveRequest(BaseModel):
    id: str
    direction: str

class MoveResponse(BaseModel):
    id: str
    x: int
    y: int
    message: str

class Paket(BaseModel):
    id: str
    pickup_x: int
    pickup_y: int
    drop_x: int
    drop_y: int
    status: str
    carried_by: Optional[str] = None

class PaketActionRequest(BaseModel):
    agent_id: str
    action: str

class PaketActionResponse(BaseModel):
    message: str
    paket_id: Optional[str] = None

class AgentStatus(BaseModel):
    id: str
    x: int
    y: int

class PaketStatus(BaseModel):
    id: str
    pickup_x: int
    pickup_y: int
    drop_x: int
    drop_y: int
    status: str
    carried_by: Optional[str] = None
    
class SystemStatus(BaseModel):
    agents: List[AgentStatus]
    pakets: List[PaketStatus]
    obstacles: List[Tuple[int,int]]

class AddPaketRequest(BaseModel):
    id: str
    pickup_x: int
    pickup_y: int
    drop_x: int
    drop_y: int

class AddPaketResponse(BaseModel):
    message: str
    paket_id: str

class GridSizeRequest(BaseModel):
    size: int
