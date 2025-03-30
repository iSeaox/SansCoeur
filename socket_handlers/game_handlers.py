from flask_socketio import emit
from flask import request
from auth import socketio_login_required
from flask_login import current_user

def register_handlers(socketio, connected_clients, gameManager):

    @socketio.on("connect")
    @socketio_login_required
    def handle_connect():
        gameManager.getGame().broadcastGameInfo()
        print("MANAGER: ", gameManager.getGame())
        # Check if player is register in a game
        if gameManager.getGame().getPlayerByName(current_user.username) != None:
            gameManager.getGame().resumePlayer(current_user.username, request.sid)

    @socketio.on('join_game')
    @socketio_login_required
    def handle_join_game(data):
        name = current_user.username
        team = data.get('team')

        if team not in [0, 1]:
            emit('join_error', {'message': 'Team doit être 0 ou 1'})
            return

        result, message = gameManager.getGame().registerPlayer(name, team, request.sid)
        if result:
            print(f'Client {name} a rejoint la Team {team}')
            emit('join_success', {'message': f'Vous avez rejoint la Team {team} !'})
            gameManager.getGame().broadcastGameInfo()
        else:
            emit('join_error', {'message': message})

    @socketio.on('start_game')
    @socketio_login_required
    def handle_start_game(data):
        result, message = gameManager.getGame().start(data["maxPoints"])
        if not(result):
            emit('start_game_error', {'message': message})
            return
        gameManager.getGame().broadcastGameInfo()

    @socketio.on('card_clicked')
    @socketio_login_required
    def handle_card_clicked(data):
        if "card_id" in data:
            player_name = current_user.username
            player = gameManager.getGame().getPlayerByName(player_name)
            if player:
                card_index = int(data['card_id'].split("card-")[-1])
                if card_index < len(player.cards):
                    card = player.cards[card_index]

                    gameManager.getGame().getCurrentRound().cardPlayed(player, card, card_index)

    @socketio.on("talk_click")
    @socketio_login_required
    def handle_talk_click(data):
        player_name = current_user.username
        player = gameManager.getGame().getPlayerByName(player_name)
        gameManager.getGame().getCurrentRound().registerTalk(player, data)

    @socketio.on("pass_click")
    @socketio_login_required
    def handle_talk_pass_click():
        player_name = current_user.username
        player = gameManager.getGame().getPlayerByName(player_name)
        if player:
            gameManager.getGame().getCurrentRound().registerTalkPass(player)

    @socketio.on("contrer_click")
    @socketio_login_required
    def handle_talk_contrer_click():
        player_name = current_user.username
        player = gameManager.getGame().getPlayerByName(player_name)
        if player:
            gameManager.getGame().getCurrentRound().registerTalkContrer(player)

    @socketio.on("sur_contrer_click")
    @socketio_login_required
    def handle_talk_sur_contrer_click():
        player_name = current_user.username
        player = gameManager.getGame().getPlayerByName(player_name)
        if player:
            gameManager.getGame().getCurrentRound().registerTalkSurContrer(player)

    @socketio.on("table_ack_click")
    @socketio_login_required
    def handle_table_ack_click():
        player_name = current_user.username
        player = gameManager.getGame().getPlayerByName(player_name)
        if player:
            gameManager.getGame().getCurrentRound().computeTableAck(player)


    @socketio.on('disconnect')
    def handle_disconnect():
        pass