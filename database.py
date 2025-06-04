from models import Paket
import time

agents = {}

obstacles = set([
    (3, 3), (3, 4), (4, 4), (2, 8), (3,8), (4,8), (7, 2), (7, 3)
])

GRID_SIZE = 10

logs = []
agent_steps = {}
paket_timestamps = {}
collisions_avoided = 0

def assign_initial_position(agent_id):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if not any(agent.x == i and agent.y == j for agent in agents.values()):
                return i,j
    return -1,-1

def move_agent(agent_id, direction):
    agent = agents.get(agent_id)
    if not agent:
        return None, "Agent not found"
    
    dx, dy = 0, 0
    if direction == "up":
        dx = -1
    elif direction == "down":
        dx = 1
    elif direction == "left":
        dy = -1
    elif direction == "right":
        dy = 1
    else:
        return None, "Arah tidak valid."
    
    new_x = max(0, min(GRID_SIZE-1, agent.x+dx))
    new_y = max(0, min(GRID_SIZE-1, agent.y+dy))

    if (new_x, new_y) in obstacles:
        return None, "Rintangan: posisi tidak bisa dilewati."

    for other in agents.values():
        if other.id != agent_id and other.x == new_x and other.y == new_y:
            global collisions_avoided
            collisions_avoided += 1
            return None, "Posisi sedang ditempati agen lain."
    
    agent.x = new_x
    agent.y = new_y
    agent_steps[agent_id] = agent_steps.get(agent_id, 0) + 1
    logs.append(f"{agent_id} move to ({new_x, new_y})")
    return agent, "Sukses bergerak."

pakets = []

def handle_paket_action(agent_id, action):
    agent = agents.get(agent_id)
    if not agent:
        return None, "Agent tidak ditemukan."
    
    for paket in pakets:
        if action == "pickup":
            if paket.status == "waiting" and paket.pickup_x == agent.x and paket.pickup_y == agent.y:
                paket.status = "picked_up"
                paket.carried_by = agent_id
                paket_timestamps[paket.id] = {"pickup_time": time.time()}
                logs.append(f"{agent_id} picked up {paket.id}")
                return paket.id, "Paket berhasil diambil."
        elif action == "deliver":
            if paket.status == "picked_up" and paket.carried_by == agent_id and paket.drop_x == agent.x and paket.drop_y == agent.y:
                paket.status = "delivered"
                paket_timestamps[paket.id]["deliver_time"] = time.time()
                logs.append(f"{agent_id} delivered {paket.id}")
                return paket.id, "Paket diantar."
    
    return None, "Tidak ada paket yang diambil atau diantar."

def add_new_paket(req_data):
    new_paket = Paket(
        id = req_data.id,
        pickup_x = req_data.pickup_x,
        pickup_y = req_data.pickup_y,
        drop_x=req_data.drop_x,
        drop_y=req_data.drop_y,
        status="waiting"
    )
    pakets.append(new_paket)
    return new_paket

def set_grid_size(size: int):
    global GRID_SIZE
    GRID_SIZE = size

def reset_system():
    agents.clear
    pakets.clear

def tick_smart():
    global collisions_avoided
    messages = []
    for agent_id, agent in agents.items():
        candidates = []
        paket = next((p for p in pakets if p.carried_by == agent_id and p.status == "picked_up"), None)

        if not paket:
            paket = next((p for p in pakets if p.status == "waiting"), None)
            if paket:
                if agent.x == paket.pickup_x and agent.y == paket.pickup_y:
                    paket.status = "picked_up"
                    paket.carried_by = agent_id
                    paket_timestamps[paket.id] = {"pickup_time": time.time()}
                    messages.append(f"{agent_id} picked up {paket.id}")
                    continue
                else:
                    target_x, target_y = paket.pickup_x, paket.pickup_y
            else:
                continue
        else:
            if agent.x == paket.drop_x and agent.y == paket.drop_y:
                paket.status = "delivered"
                paket_timestamps[paket.id]["deliver_time"] = time.time()
                messages.append(f"{agent_id} delivered {paket.id}")
                continue
            else:
                target_x, target_y = paket.drop_x, paket.drop_y

        dx = target_x - agent.x
        dy = target_y - agent.y

        if dx != 0:
            candidates.append((agent.x + (1 if dx > 0 else -1), agent.y))
        if dy != 0:
            candidates.append((agent.x, agent.y + (1 if dy > 0 else -1)))

        moved = False
        for cx, cy in candidates:
            if (cx, cy) in obstacles:
                continue
            if any(other.id != agent_id and other.x == cx and other.y == cy for other in agents.values()):
                collisions_avoided += 1
                continue

            agent.x, agent.y = cx, cy
            agent_steps[agent_id] = agent_steps.get(agent_id, 0) + 1
            messages.append(f"{agent_id} moved to ({cx},{cy})")
            moved = True
            break

        if not moved:
            messages.append(f"{agent_id} stuck (tidak bisa bergerak)")

    return messages
