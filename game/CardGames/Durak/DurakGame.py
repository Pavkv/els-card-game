# coding=utf-8

from game.CardGames.Classes.CardGame import CardGame
from game.CardGames.Classes.Table import Table
from game.CardGames.Classes.Card import Card
from game.CardGames.Classes.AIDurak import AIDurak

class DurakGame(CardGame):
    def __init__(self, player_name, opponent_name, biased_draw):
        CardGame.__init__(self, player_name, biased_draw)
        self.opponent = AIDurak(opponent_name)
        self.table = Table()

    def start_game(self, n=6, sort_hand=True):
        CardGame.start_game(self, n=n, sort_hand=sort_hand)

    def can_attack(self, attacker, num_of_attack_cards=0):
        """Check if the attacker can attack."""
        if len(attacker.hand) == 0:
            return False

        defender = self.player if attacker is self.opponent else self.opponent

        if self.table.num_unbeaten() + num_of_attack_cards > len(defender.hand):
            return False

        if len(self.table) == 0:
            return len(attacker.hand) > 0

        return any(card.rank in self.table.ranks for card in attacker.hand)

    def attack_cards(self, cards):
        """Player attacks with selected cards."""
        if not self.can_attack(self.current_turn, len(cards)):
            return False
        for card in cards:
            if card not in self.current_turn.hand or not self.table.append(card):
                for played_card in cards:
                    if played_card in self.table.table:
                        del self.table.table[played_card]
                        self.table.ranks.discard(played_card.rank)
                return False
        for card in cards:
            self.current_turn.hand.remove(card)
        return True

    def defend_card(self, defend_card, attack_card):
        """Player defends against an attack card."""
        if not Card.beats(defend_card, attack_card, self.deck.trump_suit):
            return False
        self.player.hand.remove(defend_card)
        self.table.beat(attack_card, defend_card)
        return True

    def opponent_attack(self):
        """Opponent attacks with chosen cards."""
        cards = self.opponent.choose_attack_cards(
            self.table,
            self.deck.trump_suit,
            len(self.player.hand)
        )
        if not cards:
            return False

        played = 0
        for card in cards:
            if card in self.opponent.hand and self.table.append(card):
                self.opponent.hand.remove(card)
                played += 1
        return played > 0

    def opponent_defend(self):
        """Opponent defends against all attack cards."""
        for attack_card, (beaten, _) in self.table.table.items():
            if not beaten:
                defend_card = self.opponent.defense(attack_card, self.deck.trump_suit)
                if defend_card:
                    self.opponent.hand.remove(defend_card)
                    self.table.beat(attack_card, defend_card)
                else:
                    return False
        return True

    def throw_ins(self):
        """Opponent throws in additional cards after beating all attacks."""
        throw_ins = self.opponent.choose_throw_ins(
            self.table,
            len(self.player.hand),
            self.deck.trump_suit
        )

        successful_throws = []

        for card in throw_ins:
            if self.table.append(card):
                self.opponent.hand.remove(card)
                successful_throws.append(card)

        return successful_throws

    def take_or_discard_cards(self):
        """The player who failed to defend takes all cards on the table, otherwise they are discarded."""
        if not self.table.beaten():
            receiver = self.player if self.current_turn != self.player else self.opponent
            for atk_card, (beaten, def_card) in self.table.table.items():
                receiver.hand.append(atk_card)
                if def_card:
                    receiver.hand.append(def_card)
        else:
            for atk_card, (beaten, def_card) in self.table.table.items():
                self.deck.discard.append(atk_card)
                if def_card:
                    self.deck.discard.append(def_card)
            self.current_turn = self.opponent if self.current_turn == self.player else self.player

    def check_endgame(self):
        """Check if the game is over and set the result."""
        if self.deck.cards or (len(self.player.hand) > 0 and len(self.opponent.hand) > 0):
            return
        player_cards = len(self.player.hand)
        opponent_cards = len(self.opponent.hand)
        if player_cards == 0 and player_cards == opponent_cards and self.table.beaten():
            self.result = "draw"
        elif player_cards < opponent_cards:
            self.result = self.player.name
        else:
            self.result = self.opponent.name
