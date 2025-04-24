GRAPH_TYPE_TOTAL_POINT = 0
GRAPH_TYPE_AVERAGE_POINT = 1
GRAPH_TYPE_LOOSE_TALK = 2
GRAPH_TYPE_RATIO_LOOSE_PLAYED = 3
PROFILE_STATISTIC = 4
GRAPH_PROFILE_STATISTIC = 5

COLORS_TYPE_0 = [
    "rgba(204, 92, 74)",
    "rgba(231, 111, 81)",
    "rgba(237, 136, 89)",
    "rgba(244, 162, 97)",
    "rgba(238, 179, 101)",
    "rgba(233, 196, 106)",
    "rgba(137, 176, 124)",
    "rgba(42, 157, 143)",
    "rgba(69, 105, 98)",
    "rgba(38, 70, 83)",
]

COLORS_TYPE_1 = [
    "rgba(19, 42, 19)",
    "rgba(34, 64, 31)",
    "rgba(49, 87, 44)",
    "rgba(64, 106, 45)",
    "rgba(79, 119, 45)",
    "rgba(111, 144, 65)",
    "rgba(144, 169, 85)",
    "rgba(190, 206, 122)",
    "rgba(236, 243, 158)",
    "rgba(255, 255, 200)",
]
COLORS_TYPE_2 = [
    "rgba(1, 42, 74)",
    "rgba(1, 58, 99)",
    "rgba(1, 73, 124)",
    "rgba(1, 79, 134)",
    "rgba(42, 111, 151)",
    "rgba(44, 125, 160)",
    "rgba(70, 143, 175)",
    "rgba(97, 165, 194)",
    "rgba(137, 194, 217)",
    "rgba(169, 214, 229)",
]

COLORS_TYPE_3 = [
    "rgba(84, 71, 140)",
    "rgba(44, 105, 154)",
    "rgba(4, 139, 168)",
    "rgba(13, 179, 158)",
    "rgba(22, 219, 147)",
    "rgba(131, 227, 119)",
    "rgba(185, 231, 105)",
    "rgba(239, 234, 90)",
    "rgba(241, 196, 83)",
    "rgba(242, 158, 76)",
]

DATA_MODEL = {
    "type": "",
    "data": {
        "labels": [],
        "datasets": [{
            "label": "",
            "data": [],
            "backgroundColor": [],
            "borderColor": [],
            "borderWidth": 0
        }]
    },
    "options": {
        "scales": {
            "y": {
                "beginAtZero": True,
            }
        }
    }
}

def dumpData(logManager, type, player=None):
    games = logManager.dumpGameLogs()
    out = _analyseGamesDump(games)
    if type == GRAPH_TYPE_TOTAL_POINT:
        sorted_players = dict(sorted(out["players"].items(), key=lambda item: item[1]["totalScore"], reverse=True))
        if len(sorted_players) > 10:
            sorted_players = sorted_players[:11]
        data_model = DATA_MODEL.copy()
        data_model["type"] = "bar"
        data_model["data"]["labels"] = [player for player in sorted_players.keys()]
        data_model["data"]["datasets"][0]["label"] = "Top 10 des scores totaux"
        data_model["data"]["datasets"][0]["data"] = [player_data["totalScore"] for player_data in sorted_players.values()]
        data_model["data"]["datasets"][0]["backgroundColor"] = COLORS_TYPE_0[:len(sorted_players)]
        data_model["data"]["datasets"][0]["borderColor"] = COLORS_TYPE_0[:len(sorted_players)]
        data_model["data"]["datasets"][0]["borderWidth"] = 0
        data_model["options"] = {"scales": {"y": {"beginAtZero": True,}}}

    elif type == GRAPH_TYPE_AVERAGE_POINT:
        sorted_players = dict(sorted(out["players"].items(), key=lambda item: item[1]["totalScore"] / item[1]["nbGamePlayed"], reverse=True))
        if len(sorted_players) > 10:
            sorted_players = sorted_players[:11]
        data_model = DATA_MODEL.copy()
        data_model["type"] = "bar"
        data_model["data"]["labels"] = [player for player in sorted_players.keys()]
        data_model["data"]["datasets"][0]["label"] = "Top 10 des moyennes de point par partie"
        data_model["data"]["datasets"][0]["data"] = [player_data["totalScore"] / player_data["nbGamePlayed"] for player_data in sorted_players.values()]
        data_model["data"]["datasets"][0]["backgroundColor"] = COLORS_TYPE_1[:len(sorted_players)]
        data_model["data"]["datasets"][0]["borderColor"] = COLORS_TYPE_1[:len(sorted_players)]
        data_model["data"]["datasets"][0]["borderWidth"] = 0
        data_model["options"] = {"scales": {"y": {"beginAtZero": True,}}}

    elif type == GRAPH_TYPE_LOOSE_TALK:
        sorted_players = dict(sorted(out["players"].items(), key=lambda item: item[1]["looseTalk"], reverse=True))
        if len(sorted_players) > 10:
            sorted_players = sorted_players[:11]
        data_model = DATA_MODEL.copy()
        data_model["type"] = "bar"
        data_model["data"]["labels"] = [player for player in sorted_players.keys()]
        data_model["data"]["datasets"][0]["label"] = "Top 10 des contrats ratés"
        data_model["data"]["datasets"][0]["data"] = [player_data["looseTalk"] for player_data in sorted_players.values()]
        data_model["data"]["datasets"][0]["backgroundColor"] = COLORS_TYPE_2[:len(sorted_players)]
        data_model["data"]["datasets"][0]["borderColor"] = COLORS_TYPE_2[:len(sorted_players)]
        data_model["data"]["datasets"][0]["borderWidth"] = 0
        data_model["options"] = {"scales": {"y": {"beginAtZero": True,}}}

    elif type == GRAPH_TYPE_RATIO_LOOSE_PLAYED:
        sorted_players = dict(sorted(out["players"].items(), key=lambda item: item[1]["winGame"] / item[1]["nbGamePlayed"], reverse=True))
        if len(sorted_players) > 10:
            sorted_players = sorted_players[:11]
        data_model = DATA_MODEL.copy()
        data_model["type"] = "bar"
        data_model["data"]["labels"] = [player for player in sorted_players.keys()]
        data_model["data"]["datasets"][0]["label"] = "Top 10 des ratios de victoire (%)"
        data_model["data"]["datasets"][0]["data"] = [100 * player_data["winGame"] / player_data["nbGamePlayed"] for player_data in sorted_players.values()]
        data_model["data"]["datasets"][0]["backgroundColor"] = COLORS_TYPE_3[:len(sorted_players)]
        data_model["data"]["datasets"][0]["borderColor"] = COLORS_TYPE_3[:len(sorted_players)]
        data_model["data"]["datasets"][0]["borderWidth"] = 0
        data_model["options"] = {"indexAxis": "y", "scales": {"y": {"min": 0, "max": 100}}}

    elif type == PROFILE_STATISTIC:
        return out["players"][player]

    elif type == GRAPH_PROFILE_STATISTIC:
        player_data = out["players"][player]
        data_model = DATA_MODEL.copy()

        # Create a chronological progression of the player's win ratio
        player_games = []
        win_count = 0
        game_count = 0
        ratios = []

        # Find all games with this player and sort them by time
        for g in games:
            player_in_game = False
            for p in g["players"]:
                if p["name"] == player:
                    player_in_game = True
                    break

            if player_in_game:
                game_count += 1
                player_team = None

                # Find the player's team in this game
                for p in g["players"]:
                    if p["name"] == player:
                        player_team = p["team"]
                        break

                # Check if player's team won
                if g["score"][player_team] > g["score"][not player_team]:
                    win_count += 1

                # Calculate cumulative ratio after each game
                ratio = (win_count / game_count) * 100
                ratios.append(ratio)
                player_games.append(g.get("time", f"Partie {game_count}"))

        # Set up the line chart
        data_model["type"] = "line"
        data_model["data"]["labels"] = player_games
        data_model["data"]["datasets"][0]["label"] = f"Évolution du ratio de victoire pour {player} (%)"
        data_model["data"]["datasets"][0]["data"] = ratios
        data_model["data"]["datasets"][0]["backgroundColor"] = "rgba(231, 111, 81, 0.5)"
        data_model["data"]["datasets"][0]["borderColor"] = "rgba(231, 111, 81, 1)"
        data_model["data"]["datasets"][0]["borderWidth"] = 3
        data_model["data"]["datasets"][0]["pointRadius"] = 1

        # Add specific options for line chart
        data_model["options"]["plugins"] = {
            "title": {
                "display": True,
                "text": f"Progression du ratio de victoire pour {player}"
            }
        }
        data_model["options"]["scales"]["y"]["min"] = 0
        data_model["options"]["scales"]["y"]["max"] = 100

    return data_model

def _analyseGamesDump(games):
    out = {
        "players": {},
        "playedGame": 0
    }
    for g in games:
        out["playedGame"] += 1

        playerTeam = []
        for p in g["players"]:
            currentTeam = p["team"]
            playerTeam.append((p, currentTeam))

            if not(p["name"] in out["players"]):
                out["players"][p["name"]] = {
                    "totalScore": 0,
                    "looseTalk": 0,
                    "winTalk": 0,
                    "played_round": 0,
                    "nbGamePlayed": 0,
                    "winGame": 0,
                    "timePlayed": 0
                }

            if g["score"][currentTeam] > g["score"][not(currentTeam)]:
                out["players"][p["name"]]["winGame"] += 1

            out["players"][p["name"]]["nbGamePlayed"] += 1
            out["players"][p["name"]]["totalScore"] += g["score"][currentTeam]
            if "duration" in g:
                out["players"][p["name"]]["timePlayed"] += g["duration"]

        for r in g["round_score"]:
            talkTeam = r["talk"]["team"]
            talkValue = r["talk"]["value"]
            if r["score"][talkTeam] > 80 and r["score"][talkTeam] > talkValue:
                for player, team in playerTeam:
                    out["players"][player["name"]]["played_round"] += 1
                    if team == talkTeam:
                        out["players"][player["name"]]["winTalk"] += 1
            else:
                for player, team in playerTeam:
                    out["players"][player["name"]]["played_round"] += 1
                    if team == talkTeam:
                        out["players"][player["name"]]["looseTalk"] += 1
                    else:
                        out["players"][player["name"]]["winTalk"] += 1

    # Format played time
    for player in out["players"].values():
        seconds = player["timePlayed"]
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        player["timePlayed"] = f"{int(hours)}h {int(minutes)}min {int(seconds)}s"
    return out

