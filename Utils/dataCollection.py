"""
Utility Functions for Data Collection  

Author: Phillip Kornberg
Date: 3.31.25
"""

import os
from statsbombpy import sb
import warnings
import json
from tqdm import tqdm
import pandas as pd

def APICall(competitionId, seasonId, teamName):
    """
    Function to Call StatsBomb API to Collect Data From Desired Season

    : param int competitionId - Number of Competition ID to Query
    : param int seasonId - Number of Season to Query
    : param str teamName - Name of Team to Collect Data For

    : return arr matchList - List of Files
    """

    # Supress Warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="statsbombpy")

    # Update Team Name
    updatedTeamName = teamName.replace(" ", "_")

    # Declare Save Folder
    saveFolder = os.path.join("../Data", f"{updatedTeamName}_{seasonId}")
    os.makedirs(saveFolder, exist_ok=True)

    # Find Relevant Matches
    matches = sb.matches(competition_id = competitionId, season_id = seasonId)
    teamMatches = matches[(matches.home_team == teamName) | (matches.away_team == teamName)]
    matchList = []

    # Loop Through Matches
    for idx, match in tqdm(teamMatches.iterrows(), total = len(teamMatches), desc = "Processing Games"):
        match_id = match.match_id
        events = sb.events(match_id = match_id, fmt = "dict")

        if isinstance(events, dict):
            events = list(events.values())

        filePath = os.path.join(saveFolder, f"{match_id}.json")
        with open(filePath, "w") as f:
            json.dump(events, f, indent=2)

        matchList.append(filePath)

    # Returning Match List
    return matchList

def collectDataOneGame(fileName, targetTeam):
    """
    Function to Collect Pass and Shot Data for One Team During One Game

    : param str fileName - Name of File to Collect Data 
    : param str targetTeam - Name of Team 

    : return dataFrame firstHalf - Data Frame Containing First Half Events
    : return dataFrame secondHalf - Data Frame Containing Second Half Events
    : return dict playerInfo1 - First Half Player Information
    : return dict playerInfo2 - Second Half Player Information
    """

    # Initializing Arrays
    sender1, receiver1, timestamp1, type1, xG1 = [], [], [], [], []
    sender2, receiver2, timestamp2, type2, xG2 = [], [], [], [], []

    # Initializing Player Information
    playerInfo1 = {}
    playerInfo2 = {}

    with open(fileName, "r") as f:
        data = json.load(f)

    # Helper Dictionaries to Store Positions and Names
    positions1, names1, ids1 = {}, {}, set()
    positions2, names2, ids2 = {}, {}, set()
    foundSecondHalfLineup = False

    # Collect Lineups
    for event in data:
        teamName = event.get("team", {}).get("name")
        if teamName != targetTeam:
            continue

        # First Half
        if event["period"] == 1 and "tactics" in event:
            lineup = event["tactics"].get("lineup", [])
            for p in lineup:
                pid = p["player"]["id"]
                positions1[pid] = p["position"]["name"]
                names1[pid] = p["player"]["name"]
                ids1.add(pid)

        # Second Half
        if event["period"] == 2 and "tactics" in event:
            lineup = event["tactics"].get("lineup", [])
            if lineup:
                foundSecondHalfLineup = True
                for p in lineup:
                    pid = p["player"]["id"]
                    positions2[pid] = p["position"]["name"]
                    names2[pid] = p["player"]["name"]
                    ids2.add(pid)

        # Collect Substitution Information
        if event["type"]["name"] == "Substitution":
            sub = event["substitution"]["replacement"]
            pid = sub["id"]
            name = sub["name"]
            old_pid = event["player"]["id"]
            pos = positions1.get(old_pid) if event["period"] == 1 else positions2.get(old_pid)
            if event["period"] == 1 and pid not in ids1:
                positions1[pid] = pos
                names1[pid] = name
                ids1.add(pid)
            elif event["period"] == 2 and pid not in ids2:
                positions2[pid] = pos
                names2[pid] = name
                ids2.add(pid)

    # If No Second Half Lineup, Copy First Half
    if not foundSecondHalfLineup:
        positions2, names2, ids2 = positions1.copy(), names1.copy(), ids1.copy()

    # Add Goal Node
    for positions, names, ids in [(positions1, names1, ids1), (positions2, names2, ids2)]:
        positions[-1] = "Goal"
        names[-1] = "Goal Node"
        ids.add(-1)

    # Build Player Information Dictionary
    playerInfo1[targetTeam] = {pid: {"position": positions1[pid], "name": names1[pid]} for pid in ids1}
    playerInfo2[targetTeam] = {pid: {"position": positions2[pid], "name": names2[pid]} for pid in ids2}

    # Collect Pass and Shot Events
    for event in data:
        pid = event.get("player", {}).get("id")
        time = event.get("minute", 0) * 60 + event.get("second", 0)

        # First Half
        if event["period"] == 1:
            if "pass" in event and pid in ids1:
                receiver = event["pass"].get("recipient", {}).get("id", -1)
                if receiver not in ids1:
                    receiver = -1
                sender1.append(pid)
                receiver1.append(receiver)
                timestamp1.append(time)
                type1.append("Pass")
                xG1.append(0)
            if "shot" in event and pid in ids1:
                sender1.append(pid)
                receiver1.append(-1)
                timestamp1.append(time)
                type1.append("Shot")
                xG = round(event["shot"]["statsbomb_xg"], 2)
                xG1.append(xG)

        # Second Half
        if event["period"] == 2:
            if "pass" in event and pid in ids2:
                receiver = event["pass"].get("recipient", {}).get("id", -1)
                if receiver not in ids2:
                    receiver = -1
                sender2.append(pid)
                receiver2.append(receiver)
                timestamp2.append(time)
                type2.append("Pass")
                xG2.append(0)
            if "shot" in event and pid in ids2:
                sender2.append(pid)
                receiver2.append(-1)
                timestamp2.append(time)
                type2.append("Shot")
                xG = round(event["shot"]["statsbomb_xg"], 2)
                xG2.append(xG)

    # Format Dataframes
    firstHalf = pd.DataFrame({"Sender": sender1, "Receiver": receiver1, "Timestamp": timestamp1, "Type": type1, "xG": xG1})
    secondHalf = pd.DataFrame({"Sender": sender2, "Receiver": receiver2, "Timestamp": timestamp2, "Type": type2, "xG": xG2})

    return firstHalf, secondHalf, playerInfo1, playerInfo2