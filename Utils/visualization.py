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
