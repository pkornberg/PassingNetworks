"""
Utility Functions for Passing Network Visualization

Author: Phillip Kornberg
Date: 3.31.25
"""

import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
plt.rcParams['figure.dpi'] = 1000

def createPassingNetwork(teamName, gameDfs, passThreshold, playerInformation, margin):
    """
    Function to Build Season Long Passing Network

    : param str teamName - Name of Team
    : param dataFrame gameDfs - Array of Game DataFrames from multiGameCollection()
    : param int passThreshold - Min Amount of Passes Needed for Player to be Displayed in Graph
    : param dict playerInformation - Dictionary Returned from multiGameCollection()
    : param int margin - Spacing Between Nodes

    : print Passing Network
    """

    # Creating Directed Graph
    DG = nx.MultiDiGraph()
    data = pd.concat(gameDfs, ignore_index = True)

    # Counting Passes for Filtering
    passCounts = Counter(zip(data["Sender"], data["Receiver"]))

    # Adding Edges
    for (sender, receiver), weight in passCounts.items():
        DG.add_edge(sender, receiver, weight=weight)

    # Collecting Player Last Names
    teamInfromation = playerInformation[teamName]
    lastnames = {
        details['index']: (
            'Goal' if details['name'] == 'Goal Node'
            else 'Messi' if details['name'] == 'Lionel Andrés Messi Cuccittini'
            else details['name'].split()[-1]
        )
        for pid, details in teamInfromation.items()
    }

    # Labeling and Filtering Graph
    DGLabeled = nx.relabel_nodes(DG, lastnames)

    DGFiltered = nx.MultiDiGraph()
    for sender, receiver, d in DGLabeled.edges(data=True):
        if d['weight'] >= passThreshold:
            DGFiltered.add_edge(sender, receiver, weight=d['weight'])
    isolated = list(nx.isolates(DGFiltered))
    DGFiltered.remove_nodes_from(isolated)

    # Determing GRaph Position and Edges
    pos = nx.spring_layout(DGFiltered, seed = 42, k = margin, iterations = 100)
    center = np.mean(list(pos.values()), axis = 0)
    pos = {node: (coord - center) * 1.5 + center for node, coord in pos.items()}

    edges = list(DGFiltered.edges(data = True))

    # Sorting Edges by Weight
    edges_sorted = sorted(edges, key = lambda x: x[2]['weight'])
    weights = [d['weight'] for _, _, d in edges_sorted]
    max_w = max(weights)
    widths = [3 * w / max_w for w in weights]

    # Plotting Figure
    fig, ax = plt.subplots()

    node_colors = [
        'lightcoral' if node == 'Goal' else 'lightskyblue'
        for node in DGFiltered.nodes()
    ]

    # Drawing Graph
    nx.draw_networkx_nodes(DGFiltered, pos, node_color=node_colors, edgecolors='black', node_size=650, ax=ax)
    nx.draw_networkx_labels(DGFiltered, pos, ax=ax, font_size=4.5)
    nx.draw_networkx_edges(
        DGFiltered, pos,
        edgelist = [(u, v) for u, v, _ in edges_sorted],
        width = widths,
        edge_color = weights,
        edge_cmap = plt.cm.Blues,
        arrows = True,
        arrowsize = 15,
        connectionstyle = 'arc3,rad=0.1',
        min_target_margin = margin,
        ax = ax
    )

    sm = plt.cm.ScalarMappable(cmap = plt.cm.Blues, norm = plt.Normalize(vmin = min(weights), vmax = max_w))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax = ax, shrink = 0.6)
    cbar.ax.set_title("Pass Count", pad = 8, fontsize = 8)

    plt.title(f"{teamName} Season Long Passing Network")
    ax.axis('off')
    plt.tight_layout()
    plt.show()

def playerHeatmap(dataFrames, playerID, playerName, teamName, playerInformation):
    """
    Function to Display Player Passing Heatmap

    : param arr dataFrames - List of Game DataFrames
    : param int playerID - Player ID Number
    : param str playerName - Preferred Player Name for Graphing
    : param str teamName - Name of Team
    : param dict playerInformation - Dictionary of Player Information

    : print Player Heatmap
    """

    # Finding Player ID and Name
    index = playerInformation[teamName][playerID]["index"]
    name = playerInformation[teamName][playerID]["name"]

    # Concatenating Data Frames 
    gameDfs = pd.concat(dataFrames)
    gameDfs = gameDfs[gameDfs["Sender"] == index]

    # Extracting Location Information
    gameDfs['x'] = gameDfs['Location'].apply(lambda loc: loc[0])
    gameDfs['y'] = gameDfs['Location'].apply(lambda loc: loc[1])

    # Drawing Soccer Field
    width, height = 120, 80
    cellSize = 4 
    gridW = int(np.ceil(width / cellSize))
    gridH = int(np.ceil(height / cellSize))

    grid = np.zeros((gridH, gridW))
    for _, row in gameDfs.iterrows():
        gx = min(int(row['x'] // cellSize), gridW - 1)
        gy = min(int(row['y'] // cellSize), gridH - 1)
        grid[gy, gx] += 1

    # Determining Heatmap
    heatColors = [
        (1.0, 1.0, 1.0, 0.0),    
        (0.85, 0.92, 1.0, 0.5),  
        (0.5, 0.75, 1.0, 0.7),   
        (0.2, 0.5, 0.9, 0.85),   
        (0.05, 0.2, 0.6, 1.0)    
    ]
    heatCmap = LinearSegmentedColormap.from_list('tactical_blue', heatColors)

    # Setting Up Figure
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(-5, width + 5)
    ax.set_ylim(-5, height + 5)
    ax.set_aspect('equal')
    ax.axis('off')
    norm_grid = np.power(grid / grid.max(), 0.7) if grid.max() > 0 else grid

    # Drawing Boxes
    for y in range(gridH):
        for x in range(gridW):
            val = norm_grid[y, x]
            if val > 0:
                rect_color = heatCmap(val)
                ax.add_patch(patches.Rectangle(
                    (x * cellSize, y * cellSize), cellSize, cellSize,
                    facecolor=rect_color,
                    edgecolor='white',  
                    linewidth=0.5,
                    zorder=2
                ))

    # Setting Picth Width
    LINE_KW = dict(color = "#000000", linewidth = 2.2, zorder = 3)

    # Main Field
    ax.add_patch(patches.Rectangle((0, 0), width, height, fill = False, **LINE_KW))
    ax.plot([width/2, width/2], [0, height], **LINE_KW) 
    ax.add_patch(patches.Circle((width/2, height/2), 9.15, fill = False, **LINE_KW)) 
    ax.scatter(width/2, height/2, color = 'black', s = 30, zorder = 4) 

    # Left Penalty Areas
    ax.add_patch(patches.Rectangle((0, height/2-20.15), 16.5, 40.3, fill = False, **LINE_KW))
    ax.add_patch(patches.Rectangle((0, height/2-9.15), 5.5, 18.3, fill = False, **LINE_KW))
    ax.add_patch(patches.Arc((11, height/2), 18.3, 18.3, theta1 = 308, theta2 = 52, **LINE_KW))

    # Right Penalty Areas
    ax.add_patch(patches.Rectangle((width-16.5, height/2-20.15), 16.5, 40.3, fill = False, **LINE_KW))
    ax.add_patch(patches.Rectangle((width-5.5, height/2-9.15), 5.5, 18.3, fill = False, **LINE_KW))
    ax.add_patch(patches.Arc((width-11, height/2), 18.3, 18.3, theta1 = 128, theta2 = 232, **LINE_KW))

    # Drawing Corner Kicks
    corner_details = [(0,0,0,90), (0,80,270,360), (120,0,90,180), (120,80,180,270)]
    for cx, cy, t1, t2 in corner_details:
        ax.add_patch(patches.Arc((cx, cy), 4, 4, theta1 = t1, theta2 = t2, **LINE_KW))

    # Drawing Titleand Subtitle
    ax.text(width / 2, height + 6, f'{playerName}', fontsize = 34, ha = 'center')
    ax.text(width / 2, height + 2, f'Passing Heatmap With {len(gameDfs)} Total Passes', 
            fontsize = 14, color = "#000000", ha = 'center')
    
    plt.show()
