# coding=utf-8
import random

from game.CardGames.Classes.Player import Player
from game.CardGames.Classes.Deck import Deck

class CardGame:
    def __init__(self, player_name="Вы", biased_draw=None):
        self.deck = Deck()
        self.player = Player(player_name)
        self.opponent = None
        self.first_player = None
        self.current_turn = None
        self.state = None
        self.result = None

        self.bias = {"player": 0.0, "opponent": 0.0}
        if biased_draw:
            if biased_draw[0] == "player":
                self.bias["player"] = float(biased_draw[1])
            elif biased_draw[0] == "opponent":
                self.bias["opponent"] = float(biased_draw[1])

    def start_game(self, n=6, sort_hand=False):
        self.player.draw_from_deck(self.deck, n, sort_hand, self.bias["player"])
        self.opponent.draw_from_deck(self.deck, n, sort_hand, self.bias["opponent"])
        self.first_player = random.choice([self.player, self.opponent])
        self.state = "player_turn" if self.first_player == self.player else "opponent_turn"