export const GAME_STATUS_WAITING = 0;
export const GAME_STATUS_PLAYING = 1;
export const GAME_STATUS_END = 2;

export const ROUND_STATE_SETUP = 0
export const ROUND_STATE_TALKING = 1
export const ROUND_STATE_PLAYING = 2

export const CARD_COLOR_SPADES = 0
export const CARD_COLOR_HEARTS = 1
export const CARD_COLOR_DIAMONDS = 2
export const CARD_COLOR_CLUBS = 3


export function getGameStatusText(status) {
    switch (status) {
        case GAME_STATUS_WAITING:
            return 'En attente de joueurs';
        case GAME_STATUS_PLAYING:
            return 'En cours';
        case GAME_STATUS_END:
            return 'Terminée';
        default:
            return 'Statut inconnu';
    }
}

export function getSuitName(suit) {
    switch (suit) {
        case CARD_COLOR_SPADES:
            return 'Pique';
        case CARD_COLOR_HEARTS:
            return 'Coeur';
        case CARD_COLOR_DIAMONDS:
            return 'Carreau';
        case CARD_COLOR_CLUBS:
            return 'Trèfle';
        default:
            return 'Statut inconnu';
    }
}

export function getRoundStatusText(state) {
    switch (state) {
        case ROUND_STATE_SETUP:
            return 'Distribution';
        case ROUND_STATE_TALKING:
                return 'Parlez !';
        case ROUND_STATE_PLAYING:
            return 'Jouez !';
        default:
            return 'Statut inconnu';
    }
}

export function getFormattedTalk(data) {
    let out = data.current_talk.value.toString() + " " +  getSuitName(data.current_talk.color);

    if("contrer" in data && data.contrer){
        out += " Contré"
    }

    if("surcontrer" in data && data.surcontrer){
        out += " Sur Contré"
    }

    out += " (" + data.current_talk.player + ")"

    return out
}
