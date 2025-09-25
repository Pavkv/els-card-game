# -*- coding: utf-8 -*-

from game.CardGames.Classes.CardGame import CardGame
from game.CardGames.Classes.AIWitch import AIWitch


class WitchGame(CardGame):
    """
    'Ведьма' (K♠ = Witch) — Human vs AI, 36-card deck (6..A).
    Minimal state machine with separate user/ai turns; no console I/O, no checks.
    States: idle -> player_turn/opponent_turn <-> wait_choice -> game_over

    NOTE: No automatic pair-dropping anywhere. Use drop_pairs(...) explicitly.
    """

    def __init__(self, player_name, opponent_name, biased_draw):
        CardGame.__init__(self, player_name, biased_draw)
        self.opponent = AIWitch(opponent_name)

    def game_over(self):
        if len(self.player.hand) == 0 and len(self.opponent.hand) > 1 and self.deck.is_empty():
            return True, self.player.name
        if len(self.opponent.hand) == 0 and len(self.player.hand) > 1 and self.deck.is_empty():
            return True, self.opponent.name
        if len(self.player.hand) == 1 and len(self.opponent.hand) == 1:
            if self.player.has_only_witch():
                return True, self.opponent.name
            if self.opponent.has_only_witch():
                return True, self.player.name
        return False, None
