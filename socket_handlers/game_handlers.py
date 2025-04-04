from flask_socketio import emit
from flask import request, url_for
from auth import socketio_login_required
from flask_login import current_user
import time

def register_handlers(socketio, connected_clients, gameManager):

    @socketio.on("connect")
    @socketio_login_required
    def handle_connect():
        # Check if player is register in a game
        temp_game = gameManager.getGameByPlayerName(current_user.username)
        if temp_game != None:
            temp_game.resumePlayer(current_user.username, request.sid)
            print(f'{current_user.username} est de retour')
            emit('join_success', {'message': f'{current_user.username} est de retour', "redirect": url_for('dashboard')})
            emit('launch-toast', {'message': f'Vous avez rejoint la partie !', "category": "success"})

    @socketio.on('join_game')
    @socketio_login_required
    def handle_join_game(data):
        name = current_user.username
        team = data.get('team')

        if not("id" in data):
            print("Deprecated button")
            return
        gameId = int(data.get('id'))

        if team not in [0, 1]:
            emit('join_error', {'message': 'Team doit être 0 ou 1'})
            return

        result, message = gameManager.getGameByID(gameId).registerPlayer(name, team, request.sid)
        if result:
            print(f'Client {name} a rejoint la Team {team}')
            emit('join_success', {"redirect": url_for('dashboard')})
            gameManager.getGameByID(gameId).broadcastGameInfo()
            gameManager.updateClients()
        else:
            emit('join_error', {'message': message})

    @socketio.on('quit_game')
    @socketio_login_required
    def handle_quit_game():
        name = current_user.username
        game = gameManager.getGameByPlayerName(current_user.username)
        if game:
            result, message = game.removePlayer(name)
            if result:
                print(f'Client {name} a quitté la game')
                emit("quit_success")
                game.broadcastGameInfo()
                gameManager.updateClients()

    @socketio.on('start_game')
    @socketio_login_required
    def handle_start_game(data):
        game = gameManager.getGameByPlayerName(current_user.username)
        if game:
            result, message = game.start(data["maxPoints"])
            if not(result):
                emit('start_game_error', {'message': message})
                emit('launch-toast', {'message': message, "category": "danger"})
                return
            emit('launch-toast', {'message': "Lancement de la partie", "category": "success"}, broadcast=True)
            game.broadcastGameInfo()
            gameManager.updateClients()

    @socketio.on('card_clicked')
    @socketio_login_required
    def handle_card_clicked(data):
        if "card_id" in data:
            player_name = current_user.username
            game = gameManager.getGameByPlayerName(player_name)
            if game:
                player = game.getPlayerByName(player_name)
                if player:
                    card_index = int(data['card_id'].split("card-")[-1])
                    if card_index < len(player.cards):
                        card = player.cards[card_index]

                        error = game.getCurrentRound().cardPlayed(player, card, card_index)
                        if error:
                            emit('launch-toast', error)

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

    @socketio.on('request_games_update')
    @socketio_login_required
    def handle_request_games_update():
        games = gameManager.getGames()
        emit('update_games', {'games': games})

    @socketio.on('chat_message')
    @socketio_login_required
    def handle_request_games_update(data):
        player_name = current_user.username
        game = gameManager.getGameByPlayerName(player_name)
        if game:
            player = game.getPlayerByName(player_name)
            if player:
                game.chat.registerChat(player, data)

    @socketio.on('disconnect')
    def handle_disconnect():
        pass