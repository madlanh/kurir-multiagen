import matplotlib.pyplot as plt
import matplotlib.patches as patches
from database import agents, pakets, GRID_SIZE, obstacles, agent_paths 

def draw_grid():
    print("DEBUG: Memulai draw_grid()") 
    print(f"DEBUG: agent_paths: {agent_paths}") 
    print(f"DEBUG: agents: {agents}") 
    
    fig, ax = plt.subplots(figsize=(8, 8)) 
    ax.set_xlim(-0.5, GRID_SIZE - 0.5)
    ax.set_ylim(-0.5, GRID_SIZE - 0.5)
    ax.set_xticks(range(GRID_SIZE))
    ax.set_yticks(range(GRID_SIZE))
    ax.grid(True, lw=0.5, color='gray')

    for obs_x, obs_y in obstacles:
        ax.add_patch(patches.Rectangle(
            (obs_y - 0.5, obs_x - 0.5), 1, 1, 
            facecolor='black',
            zorder=2 
        ))
        ax.text(obs_y, obs_x, 'X', ha='center', va='center', color='white', fontsize=10, weight='bold', zorder=3)

    path_colors = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'brown']
    agent_id_list = list(agents.keys()) 

    for i, agent_id in enumerate(agent_id_list):
        path = agent_paths.get(agent_id)
        if path and len(path) > 1:
            color = path_colors[i % len(path_colors)]
            for k in range(len(path) - 1):
                start_node = path[k]  
                end_node = path[k+1]    
                
                if start_node == end_node:
                    continue

                arrow = patches.FancyArrowPatch(
                    (start_node[1], start_node[0]), 
                    (end_node[1], end_node[0]),    
                    arrowstyle='->', 
                    mutation_scale=12,
                    color=color, 
                    lw=1, 
                    shrinkA=5,
                    shrinkB=5,
                    zorder=4 
                )
                ax.add_patch(arrow)

    for i, agent_id in enumerate(agent_id_list):
        if agent_id not in agents: continue
        agent = agents[agent_id]
        color = path_colors[i % len(path_colors)]
        ax.add_patch(patches.Rectangle(
            (agent.y - 0.4, agent.x - 0.4), 0.8, 0.8,
            edgecolor=color, facecolor='skyblue', alpha=0.9,
            zorder=10 
        ))
        ax.text(agent.y, agent.x, agent.id,
                ha='center', va='center', color='black', fontsize=8, weight='bold',
                zorder=11) 

    for paket in pakets:
        pos_x_grid, pos_y_grid = -1, -1
        paket_color = "grey" 
        paket_char = "?"    

        if paket.status == "waiting":
            paket_color = "orange"
            pos_x_grid, pos_y_grid = paket.pickup_x, paket.pickup_y
            paket_char = "P" 
        elif paket.status == "picked_up":
            paket_color = "lightgreen" 
            if paket.carried_by in agents: 
                carrier_agent = agents[paket.carried_by]
                pos_x_grid, pos_y_grid = carrier_agent.x, carrier_agent.y
            else: 
                continue 
            paket_char = paket.id[0].upper() if paket.id else "K" 
        elif paket.status == "delivered":
            paket_color = "darkgrey"
            pos_x_grid, pos_y_grid = paket.drop_x, paket.drop_y
            paket_char = "D" 
        else: 
            continue
        
        if pos_x_grid != -1 :
            ax.add_patch(patches.Circle(
                (pos_y_grid, pos_x_grid), 0.3, 
                color=paket_color, alpha=0.8,
                zorder=5 
            ))
            ax.text(pos_y_grid, pos_x_grid, paket_char,
                    ha='center', va='center', fontsize=7, color='black', weight='bold',
                    zorder=6) 

    ax.set_xlabel("Kolom (Y)")
    ax.set_ylabel("Baris (X)")
    ax.set_title(f"Peta Agen & Paket ({GRID_SIZE}x{GRID_SIZE})")
    
    plt.gca().invert_yaxis() 
    plt.tight_layout() 
    plt.show()
