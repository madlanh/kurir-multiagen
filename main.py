from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from models import Agent, RegisterRequest, RegisterResponse, MoveRequest, MoveResponse, PaketActionRequest, PaketActionResponse, SystemStatus, AgentStatus, PaketStatus, AddPaketRequest, AddPaketResponse, GridSizeRequest
import database
from database import handle_paket_action, add_new_paket
from visualisasi import draw_grid

app = FastAPI()

@app.get("/", include_in_schema=False)
def redirect_to_dashboard():
    return RedirectResponse(url="/dashboard")

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

@app.post("/move", response_model=MoveResponse)
def move_agent(req: MoveRequest):
    agent, msg = database.move_agent(req.id, req.direction)
    if agent is None:
        raise HTTPException(status_code=400, detail=msg)
    
    return MoveResponse(id=agent.id, x=agent.x, y=agent.y, message=msg)

@app.post("/paket", response_model=PaketActionResponse)
def paket_action(req: PaketActionRequest):
    paket_id, msg = handle_paket_action(req.agent_id, req.action)
    return PaketActionResponse(message=msg, paket_id=paket_id)

@app.get("/agents")
def get_all_agents():
    return {k: {"x": v.x, "y": v.y} for k, v in database.agents.items()}

@app.get("/status", response_model=SystemStatus)
def get_system_status():
    agent_list = [
        AgentStatus(id=a.id, x=a.x, y=a.y)
        for a in database.agents.values()
    ]

    paket_list = [
        PaketStatus(
            id=p.id,
            pickup_x=p.pickup_x,
            pickup_y=p.pickup_y,
            drop_x=p.drop_x,
            drop_y=p.drop_y,
            status=p.status,
            carried_by=p.carried_by
        ) for p in database.pakets
    ]

    return SystemStatus(
        agents=agent_list,
        pakets=paket_list,
        obstacles=list(database.obstacles)
    )

@app.get("/map")
def show_map():
    draw_grid()
    return {"message": "Map ditampilkan."}

@app.get("/dashboard")
def get_dashboard():
    return FileResponse("static/index.html")

@app.post("/add_paket", response_model=AddPaketResponse)
def add_paket(req: AddPaketRequest):
    if any(p.id == req.id for p in database.pakets):
        raise HTTPException(status_code=400, detail="Paket sudah ada.")
    
    paket = database.add_new_paket(req)
    return AddPaketResponse(message="Paket berhasil ditambahkan.", paket_id=paket.id)

@app.post("/reset")
def reset_simulasi():
    database.agents.clear()
    database.pakets.clear()
    return {"message": "Sistem berhasil direset."}

@app.post("/grid_size")
def change_grid_size(req: GridSizeRequest):
    if req.size not in [5,10]:
        raise HTTPException(status_code=400, detail="Ukuran hanya bisa 5 atau 10.")
    database.set_grid_size(req.size)
    database.reset_system()
    return {"message": f"Ukuran peta diubah menjadi {req.size}x{req.size} dan sistem di-reset."}
