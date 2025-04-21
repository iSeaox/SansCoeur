from flask_socketio import emit
from flask import request, url_for
from auth import socketio_login_required
from flask_login import current_user
import statisticManager
import re

def register_handlers(socketio, logManager, gameManager):

    @socketio.on("connect")
    @socketio_login_required
    def handle_connect():
        print(f"{current_user.username} est connecté avec le SID {request.sid}")

        # Check if player is register in a game
        temp_game = gameManager.getGameByPlayerName(current_user.username)
        if temp_game != None:
            if temp_game.resumePlayer(current_user.username, request.sid):
                emit("join_success", {"message": "Redirection vers la page de jeu", "redirect": url_for("dashboard", id=temp_game.id)})

    @socketio.on("connect_game")
    @socketio_login_required
    def handle_connect_game(data):
        player_name = current_user.username
        if "id" in data:
            gameId = int(data["id"])
            game = gameManager.getGameByID(gameId)
            if game:
                gameManager.roomManager.add_player_to_room(f"game-{gameId}", player_name, request.sid)
                game.broadcastGameInfo()
                round = game.getCurrentRound()
                if round:
                    round.sendRoundInfo()
                    player = game.getPlayerByName(player_name)
                    if player:
                        player.sendDeck()

            # Verify if the player belongs to the game
            if game and game.getPlayerByName(player_name):
                r_manager = gameManager.roomManager
                r_manager.broadcast_to_room(f"game-{game.id}", "launch-toast", {"message": f"{current_user.username} est de retour", "category": "success"})
            else:
                r_manager = gameManager.roomManager
                r_manager.add_player_to_room(f"game-{gameId}-spec", player_name, request.sid)
                r_manager.broadcast_to_room(request.sid, "load-spec-tools", {})
                r_manager.broadcast_to_room(f"game-{game.id}", "launch-toast", {"message": f"{current_user.username} regarde la partie", "category": "success"})

    @socketio.on("join_game")
    @socketio_login_required
    def handle_join_game(data):
        name = current_user.username
        team = data.get("team")
        if "id" not in data:
            return  # Deprecated button
        gameId = int(data.get("id"))
        if team not in [0, 1]:
            emit("join_error", {"message": "Team doit être 0 ou 1"})
            return

        result, message = gameManager.getGameByID(gameId).registerPlayer(name, team, request.sid)
        if result:
            print(f"Client {name} a rejoint la Team {team}")
            emit("join_success", {"redirect": url_for("dashboard", id=gameId)})
            gameManager.getGameByID(gameId).broadcastGameInfo()
            gameManager.updateClients()
        else:
            emit("join_error", {"message": message})

    @socketio.on("quit_game")
    @socketio_login_required
    def handle_quit_game():
        name = current_user.username
        game = gameManager.getGameByPlayerName(current_user.username)
        if game:
            result, message = game.removePlayer(name)
            if result:
                print(f"Client {name} a quitté la game")
                emit("quit_success")
                gameManager.roomManager.remove_player_from_room(f"game-{game.id}", name, request.sid)
                game.broadcastGameInfo()
                gameManager.updateClients()

    @socketio.on("start_game")
    @socketio_login_required
    def handle_start_game(data):
        game = gameManager.getGameByPlayerName(current_user.username)
        if game:
            result, message = game.start(data["maxPoints"])
            if not result:
                emit("start_game_error", {"message": message})
                emit("launch-toast", {"message": message, "category": "danger"})
                return
            r_manager = gameManager.roomManager
            r_manager.broadcast_to_room(f"game-{game.id}", "launch-toast",{"message": "Lancement de la partie", "category": "success"})
            game.broadcastGameInfo()
            gameManager.updateClients()

    @socketio.on("card_clicked")
    @socketio_login_required
    def handle_card_clicked(data):
        if "card_id" in data:
            player_name = current_user.username
            game = gameManager.getGameByPlayerName(player_name)
            if game:
                player = game.getPlayerByName(player_name)
                if player:
                    card_index = int(data["card_id"].split("card-")[-1])
                    if card_index < len(player.cards):
                        card = player.cards[card_index]

                        error = game.getCurrentRound().cardPlayed(player, card, card_index)
                        if error:
                            emit("launch-toast", error)

    @socketio.on("talk_click")
    @socketio_login_required
    def handle_talk_click(data):
        player_name = current_user.username
        game = gameManager.getGameByPlayerName(player_name)
        if game:
            player = game.getPlayerByName(player_name)
            if player:
                game.getCurrentRound().registerTalk(player, data)

    @socketio.on("pass_click")
    @socketio_login_required
    def handle_talk_pass_click():
        player_name = current_user.username
        game = gameManager.getGameByPlayerName(player_name)
        if game:
            player = game.getPlayerByName(player_name)
            if player:
                game.getCurrentRound().registerTalkPass(player)

    @socketio.on("contrer_click")
    @socketio_login_required
    def handle_talk_contrer_click():
        player_name = current_user.username
        game = gameManager.getGameByPlayerName(player_name)
        if game:
            player = game.getPlayerByName(player_name)
            if player:
                game.getCurrentRound().registerTalkContrer(player)

    @socketio.on("sur_contrer_click")
    @socketio_login_required
    def handle_talk_sur_contrer_click():
        player_name = current_user.username
        game = gameManager.getGameByPlayerName(player_name)
        if game:
            player = game.getPlayerByName(player_name)
            if player:
                game.getCurrentRound().registerTalkSurContrer(player)

    @socketio.on("table_ack_click")
    @socketio_login_required
    def handle_table_ack_click():
        player_name = current_user.username
        game = gameManager.getGameByPlayerName(player_name)
        if game:
            player = game.getPlayerByName(player_name)
            if player:
                currentRound = game.getCurrentRound()
                if currentRound:
                    currentRound.computeTableAck(player)

    @socketio.on("request_games_update")
    @socketio_login_required
    def handle_request_games_update():
        games = gameManager.getGames()
        emit("update_games", {"games": games})

    @socketio.on("chat_message")
    @socketio_login_required
    def handle_chat_message(data):
        player_name = current_user.username
        game = gameManager.getGameByPlayerName(player_name)
        if game:
            player = game.getPlayerByName(player_name)
            if player:
                if "gif_url" in data:
                    game.chat.registerGif(player, data["gif_url"])
                else:
                    game.chat.registerChat(player, data)
                return
        # Check if the player is in a spectator room
        player_rooms = gameManager.roomManager.get_player_rooms()
        for room in player_rooms:
            match = re.match(r'game-(\d+)-spec', room)
            if match:
                game_id = int(match.group(1))
                game = gameManager.getGameByID(game_id)
                if game:
                    if "gif_url" in data:
                        game.chat.registerSpecGif(player_name, request.sid, data["gif_url"])
                    else:
                        game.chat.registerSpecChat(player_name, request.sid, data)
                    return

    @socketio.on("request_stat_update")
    @socketio_login_required
    def handle_request_games_update(data):
        emit("stat_update", {"data": statisticManager.dumpData(logManager, data["type"]), "type": data["type"]})

    @socketio.on("request_last_game_data")
    @socketio_login_required
    def handle_request_last_game_data():
        emit("last_game_data_update", logManager.getLastGameData())

    @socketio.on("disconnect")
    @socketio_login_required
    def handle_disconnect():
        # sidManager.removeMapping(request.sid)
        pass
