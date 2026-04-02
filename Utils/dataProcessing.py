"""
Utility Functions for Data Processing

Author: Phillip Kornberg
Date: 3.31.25
"""

from Utils.dataCollection import collectDataOneGame
import pandas as pd

def buildGlobalPlayerDict(matches, teamName):
    """
    Function to Build Gloabl Player Dictionary for Consistent Player Mapping

    : param arr matches - List of File Paths to All Matches
    : param str teamName - Name of Team

    : return dict globalPlayers - Dictionary of Player Mappings
    """

    # Initializing Global Players Dictionary 
    globalPlayers = {teamName: {}}

    # Looping Through Matches
    for match in matches:
        _, _, playerInfo1, playerInfo2 = collectDataOneGame(match, teamName)

        teamPlayers = {}
        teamPlayers.update(playerInfo1.get(teamName, {}))
        teamPlayers.update(playerInfo2.get(teamName, {}))

        globalPlayers[teamName].update(teamPlayers)

    # Assigning Mapping
    players = globalPlayers[teamName]
    sortedIDs = sorted(pid for pid in players if pid != -1)

    for idx, pid in enumerate(sortedIDs):
        players[pid]["index"] = idx

    # Giving Goal Node New Index
    goalIndex = len(sortedIDs)
    players[-1]["index"] = goalIndex

    return globalPlayers

def multiGameCollection(matches, teamName, globalPlayerDict = None):
    """
    Function to Collect Data Across Multiple Matches

    : param arr matches - List of File Paths to All Matches
    : param str teamName - Name of Team

    : return df gameDfs - Array of Data Frames (One For Each Game)
    : return dict globalPlayerDict - Dictionary of Mapping
    """

    # Initializing Array
    gameDfs = []

    # Building Global Player Dictionary
    if globalPlayerDict is None:
        globalPlayerDict = buildGlobalPlayerDict(matches, teamName)

    # Build Player Mapping (ID to Index)
    newDict = {pid: info["index"] for pid, info in globalPlayerDict[teamName].items()}

    # Processing Each Match
    for match in matches:
        firstHalf, secondHalf, _, _ = collectDataOneGame(match, teamName)
        
        # Offseting Second Half Time
        secondHalf["Timestamp"] = secondHalf["Timestamp"] + 600
        matchDf = pd.concat([firstHalf, secondHalf], ignore_index = True)

        # Mapping Player ID to Indexes Consistently
        matchDf["Sender"] = matchDf["Sender"].map(newDict)
        matchDf["Receiver"] = matchDf["Receiver"].map(newDict)

        # Dropping Rows that Can't Be Mapped
        matchDf = matchDf.dropna(subset=["Sender", "Receiver"])

        # Convert indices to int
        matchDf["Sender"] = matchDf["Sender"].astype(int)
        matchDf["Receiver"] = matchDf["Receiver"].astype(int)

        gameDfs.append(matchDf)

    return gameDfs, globalPlayerDict
