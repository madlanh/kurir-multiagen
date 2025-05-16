agents = {}

GRID_SIZE = 10

def assign_initial_position(agent_id):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if not any(agent.x == i and agent.y == j for agent in agents.values()):
                return i,j
    return -1,-1