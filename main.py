from fastapi import FastAPI, HTTPException
from models import Agent, RegisterRequest, RegisterResponse
import database

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Platform Kurir Multi-Agen Siap"}

@app.post("/register", response_model=RegisterResponse)
def register_agent(req: RegisterRequest):
    if req.id in database.agents:
        raise HTTPException(status_code=400, detail="Agent sudah terdaftar.")
    
    x,y = database.assign_initial_position(req.id)

    if x == -1:
        raise HTTPException(status_code=500, detail="Tidak ada ruang tersedia.")
    
    new_agent = Agent(id=req.id, x=x, y=y)
    database.agents[req.id] = new_agent

    return RegisterResponse(id=req.id, x=x, y=y, message="Berhasil mendaftar!")