import matplotlib.pyplot as plt
import matplotlib.patches as patches
from database import agents, pakets, GRID_SIZE

def draw_grid():
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_xlim(0, GRID_SIZE)
    ax.set_ylim(0, GRID_SIZE)

    for x in range(GRID_SIZE + 1):
        ax.axhline(x, lw=0.5, color='gray')
        ax.axvline(x, lw=0.5, color='gray')

    for agent in agents.values():
        ax.add_patch(patches.Rectangle(
            (agent.y + 0.1, GRID_SIZE - 1 - agent.x + 0.1), 0.8, 0.8,
            edgecolor='blue', facecolor='skyblue'
        ))
        ax.text(agent.y + 0.5, GRID_SIZE - 1 - agent.x + 0.5, agent.id,
                ha='center', va='center', color='black', fontsize=8)

    for paket in pakets:
        if paket.status == "waiting":
            color = "orange"
            pos_x, pos_y = paket.pickup_x, paket.pickup_y
        elif paket.status == "picked_up":
            color = "green"
            if paket.carried_by in agents:
                pos_x = agents[paket.carried_by].x
                pos_y = agents[paket.carried_by].y
            else:
                continue
        elif paket.status == "delivered":
            color = "gray"
            pos_x, pos_y = paket.drop_x, paket.drop_y
        else:
            continue
        ax.add_patch(patches.Circle(
            (pos_y + 0.5, GRID_SIZE - 1 - pos_x + 0.5), 0.3,
            color=color, alpha=0.7
        ))
        ax.text(pos_y + 0.5, GRID_SIZE - 1 - pos_x + 0.5,
                paket.id, ha='center', va='center', fontsize=6, color='black')

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Peta Agen & Paket")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
