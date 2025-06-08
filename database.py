from models import Paket, AddPaketRequest
import time
import random

agents = {}
agent_paths = {}

obstacles = set([
    (3, 3), (3, 4), (4, 4), (2, 8), (3,8), (4,8), (7, 2), (7, 3)
])

GRID_SIZE = 10

logs = []
agent_steps = {}
paket_timestamps = {}
collisions_avoided = 0

def _check_move_validity(x, y, agent_id):
    if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
        return 'OUT_OF_BOUNDS'
    if (x, y) in obstacles:
        return 'OBSTACLE'
    for other_agent_id, other_agent in agents.items():
        if other_agent_id != agent_id and other_agent.x == x and other_agent.y == y:
            return 'AGENT'
    return 'VALID'

def _execute_move(agent, new_x, new_y, current_pos_x, current_pos_y):
    agent.x = new_x
    agent.y = new_y
    agent_steps[agent.id] = agent_steps.get(agent.id, 0) + 1
    logs.append(f"{agent.id} moved to ({new_x},{new_y})")

    if agent.id not in agent_paths:
        agent_paths[agent.id] = [(current_pos_x, current_pos_y)]
    last_pos = agent_paths[agent.id][-1] if agent_paths[agent.id] else None
    if last_pos != (new_x, new_y):
        agent_paths[agent.id].append((new_x, new_y))

def assign_initial_position(agent_id):
    initial_x, initial_y = -1, -1
    possible_positions = []
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if (r, c) not in obstacles and not any(agent.x == r and agent.y == c for agent in agents.values()):
                possible_positions.append((r, c))
    
    if possible_positions:
        initial_x, initial_y = random.choice(possible_positions)
        agent_paths[agent_id] = [(initial_x, initial_y)]
        return initial_x, initial_y
    return -1, -1


def move_agent(agent_id, direction):
    agent = agents.get(agent_id)
    if not agent:
        return None, "Agent not found"
    
    current_x, current_y = agent.x, agent.y

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
    
    new_x = max(0, min(GRID_SIZE - 1, agent.x + dx))
    new_y = max(0, min(GRID_SIZE - 1, agent.y + dy))

    validity = _check_move_validity(new_x, new_y, agent_id)

    if validity == 'VALID':
        _execute_move(agent, new_x, new_y, current_x, current_y)
        return agent, "Sukses bergerak."
    elif validity == 'AGENT':
        global collisions_avoided
        collisions_avoided += 1
        return None, "Posisi sedang ditempati agen lain."
    elif validity == 'OBSTACLE':
        return None, "Rintangan menghalangi."
    else:
        return None, "Batas peta menghalangi."

pakets = []

def handle_paket_action(agent_id, action):
    agent = agents.get(agent_id)
    if not agent:
        return None, "Agent tidak ditemukan."
    
    if action == "pickup":
        for paket in pakets:
            if paket.status == "waiting" and paket.pickup_x == agent.x and paket.pickup_y == agent.y:
                paket.status = "picked_up"
                paket.carried_by = agent_id
                paket_timestamps[paket.id] = {"pickup_time": time.time()}
                logs.append(f"{agent_id} picked up {paket.id}")
                return paket.id, "Paket berhasil diambil."
        return None, "Tidak ada paket untuk diambil di lokasi ini."

    elif action == "deliver":
        for paket in pakets:
            if paket.status == "picked_up" and paket.carried_by == agent_id and paket.drop_x == agent.x and paket.drop_y == agent.y:
                paket.status = "delivered"
                if paket.id in paket_timestamps:
                    paket_timestamps[paket.id]["deliver_time"] = time.time()
                else:
                    paket_timestamps[paket.id] = {"deliver_time": time.time()}
                logs.append(f"{agent_id} delivered {paket.id}")
                return paket.id, "Paket diantar."
        return None, "Tidak ada paket yang dibawa atau lokasi antar salah."
    
    return None, f"Aksi '{action}' tidak dikenal."


def add_new_paket(req: AddPaketRequest):
    possible_positions = []
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if (r, c) not in obstacles:
                possible_positions.append((r, c))

    if len(possible_positions) < 2:
        return None
    
    pickup_pos, drop_pos = random.sample(possible_positions, 2)

    pickup_x, pickup_y = pickup_pos
    drop_x, drop_y = drop_pos

    new_paket = Paket(
        id = req.id,
        pickup_x = pickup_x,
        pickup_y = pickup_y,
        drop_x=drop_x,
        drop_y=drop_y,
        status="waiting"
    )
    pakets.append(new_paket)
    return new_paket

def set_grid_size(size: int):
    global GRID_SIZE
    GRID_SIZE = size

def reset_system():
    agents.clear()
    pakets.clear()
    agent_paths.clear() 
    agent_steps.clear() 
    logs.clear()        
    paket_timestamps.clear()
    global collisions_avoided
    collisions_avoided = 0

def tick_smart():
    global collisions_avoided
    messages = []
    agent_ids_order = list(agents.keys())
    random.shuffle(agent_ids_order)

    for agent_id in agent_ids_order:
        agent = agents[agent_id]
        current_x, current_y = agent.x, agent.y
        action_taken_this_tick = False
        target_x, target_y = -1, -1 

        paket_dibawa = next((p for p in pakets if p.carried_by == agent_id and p.status == "picked_up"), None)

        if paket_dibawa:
            if agent.x == paket_dibawa.drop_x and agent.y == paket_dibawa.drop_y:
                paket_dibawa.status = "delivered"
                if paket_dibawa.id in paket_timestamps:
                    paket_timestamps[paket_dibawa.id]["deliver_time"] = time.time()
                logs.append(f"{agent_id} delivered {paket_dibawa.id}")
                messages.append(f"{agent_id} delivered {paket_dibawa.id}")
                action_taken_this_tick = True
            else:
                target_x, target_y = paket_dibawa.drop_x, paket_dibawa.drop_y
        else:
            paket_tersedia_di_lokasi = next((p for p in pakets if p.status == "waiting" and p.pickup_x == agent.x and p.pickup_y == agent.y), None)
            if paket_tersedia_di_lokasi:
                paket_tersedia_di_lokasi.status = "picked_up"
                paket_tersedia_di_lokasi.carried_by = agent_id
                paket_timestamps[paket_tersedia_di_lokasi.id] = {"pickup_time": time.time()}
                logs.append(f"{agent_id} picked up {paket_tersedia_di_lokasi.id}")
                messages.append(f"{agent_id} picked up {paket_tersedia_di_lokasi.id}")
                action_taken_this_tick = True
            else:
                closest_paket_to_pickup = next((p for p in pakets if p.status == "waiting"), None)
                if closest_paket_to_pickup:
                    target_x, target_y = closest_paket_to_pickup.pickup_x, closest_paket_to_pickup.pickup_y
                else:
                    messages.append(f"{agent_id} tidak ada tugas.")
                    continue

        if action_taken_this_tick or (target_x == -1 and target_y == -1):
            continue

        moved_in_tick = False

        delta_x = target_x - agent.x
        delta_y = target_y - agent.y

        possible_moves = []
        if abs(delta_x) > abs(delta_y):
            if delta_x != 0: possible_moves.append((agent.x + (1 if delta_x > 0 else -1), agent.y))
            if delta_y != 0: possible_moves.append((agent.x, agent.y + (1 if delta_y > 0 else -1)))
        else:
            if delta_y != 0: possible_moves.append((agent.x, agent.y + (1 if delta_y > 0 else -1)))
            if delta_x != 0: possible_moves.append((agent.x + (1 if delta_x > 0 else -1), agent.y))
        
        for next_x, next_y in possible_moves:
            validity = _check_move_validity(next_x, next_y, agent_id)
            if validity == 'VALID':
                _execute_move(agent, next_x, next_y, current_x, current_y)
                messages.append(f"{agent_id} bergerak menuju target ke ({next_x},{next_y})")
                moved_in_tick = True
                break
            elif validity == 'AGENT':
                collisions_avoided += 1
        
        if moved_in_tick:
            continue

        if not moved_in_tick:
            messages.append(f"{agent_id} mencoba mencari jalan lain...")
            all_possible_moves = [(agent.x, agent.y + 1), (agent.x, agent.y - 1), (agent.x + 1, agent.y), (agent.x - 1, agent.y)]
            random.shuffle(all_possible_moves)

            for alt_x, alt_y in all_possible_moves:
                if (alt_x, alt_y) in possible_moves:
                    continue

                validity = _check_move_validity(alt_x, alt_y, agent_id)
                if validity == 'VALID':
                    _execute_move(agent, alt_x, alt_y, current_x, current_y)
                    messages.append(f"{agent_id} terhalang, bergerak ke samping ke ({alt_x},{alt_y})")
                    moved_in_tick = True
                    break
                elif validity == 'AGENT':
                    collisions_avoided += 1

        if not moved_in_tick:
            messages.append(f"{agent_id} terperangkap dan tidak bisa bergerak.")
            
    return messages
