# coding=utf-8
import random

from game.CardGames.Classes.Card import Card
from game.CardGames.Classes.Player import Player
from game.CardGames.Classes.Deck import Deck
from game.CardGames.Classes.AIEls import AIEls

class ElsGame:
    def __init__(self, player_name="Вы", opponent_name="Противник", biased_draw=None):
        self.deck = Deck()
        self.player = Player(player_name)
        self.opponent = AIEls(opponent_name)
        self.first_player = None
        self.current_turn = None
        self.state = None
        self.round = 0
        self.turn = 0
        self.result = None

        self.bias = {"player": 0.0, "opponent": 0.0}
        if biased_draw:
            if biased_draw[0] == "player":
                self.bias["player"] = float(biased_draw[1])
            elif biased_draw[0] == "opponent":
                self.bias["opponent"] = float(biased_draw[1])

    # ---------- internals ----------
    def _draw_one(self, who):
        prob = self.bias["player"] if who is self.player else self.bias["opponent"]
        c = self.deck.draw_with_bias(prob) if prob > 0.0 else self.deck.draw_top()
        if c is not None:
            who.hand.append(c)
        return c

    def _deal_each(self):
        for _ in range(6):
            self._draw_one(self.player)
            self._draw_one(self.opponent)

    def _evaluate_hand(self, cards):
        ranks = [card.rank for card in cards]
        suits = [card.suit for card in cards]

        rank_order = Card.rank_values

        # Manually count ranks and suits
        rank_counts = {}
        suit_counts = {}
        for r in ranks:
            rank_counts[r] = rank_counts.get(r, 0) + 1
        for s in suits:
            suit_counts[s] = suit_counts.get(s, 0) + 1

        # Convert to rank values
        rank_values = sorted([rank_order[r] for r in ranks], reverse=True)

        def is_straight(values):
            values = sorted(list(set(values)), reverse=True)
            for i in range(len(values) - 4):
                window = values[i:i + 5]
                if window == list(range(window[0], window[0] - 5, -1)):
                    return True, window
            return False, []

        # Detect flush
        flush_suit = None
        for suit in suit_counts:
            if suit_counts[suit] >= 5:
                flush_suit = suit
                break

        flush_values = []
        if flush_suit:
            flush_values = [rank_order[card.rank] for card in cards if card.suit == flush_suit]
            flush_values.sort(reverse=True)

        # Detect straight and straight flush
        is_straight_all, straight_vals = is_straight(rank_values)
        is_straight_flush, straight_flush_vals = False, []
        if flush_suit:
            is_straight_flush, straight_flush_vals = is_straight(flush_values)

        # Build reverse frequency dict: freq -> [ranks]
        freq_map = {}  # freq: list of rank values
        for rank in rank_counts:
            count = rank_counts[rank]
            val = rank_order[rank]
            if count not in freq_map:
                freq_map[count] = []
            freq_map[count].append(val)

        # Sort each frequency list high to low
        for freq in freq_map:
            freq_map[freq].sort(reverse=True)

        def hand(name, rank, tiebreakers):
            return name, rank, tiebreakers

        if is_straight_flush and max(straight_flush_vals) == rank_order['A']:
            return hand("Royal Flush", 10, [rank_order['A']])
        elif is_straight_flush:
            return hand("Straight Flush", 9, straight_flush_vals)
        elif 4 in freq_map:
            four = freq_map[4][0]
            kickers = [v for v in rank_values if v != four]
            return hand("Four of a Kind", 8, [four] + kickers[:1])
        elif 3 in freq_map and 2 in freq_map:
            return hand("Full House", 7, [freq_map[3][0], freq_map[2][0]])
        elif flush_suit:
            return hand("Flush", 6, flush_values[:5])
        elif is_straight_all:
            return hand("Straight", 5, straight_vals)
        elif 3 in freq_map:
            three = freq_map[3][0]
            kickers = [v for v in rank_values if v != three]
            return hand("Three of a Kind", 4, [three] + kickers[:2])
        elif 2 in freq_map and len(freq_map[2]) >= 2:
            pairs = freq_map[2][:2]
            kicker = [v for v in rank_values if v not in pairs][0]
            return hand("Two Pair", 3, pairs + [kicker])
        elif 2 in freq_map:
            pair = freq_map[2][0]
            kickers = [v for v in rank_values if v != pair]
            return hand("One Pair", 2, [pair] + kickers[:3])
        else:
            return hand("High Card", 1, rank_values[:5])

    # ---------- externals ----------
    def start_game(self):
        self._deal_each()
        self.first_player = random.choice([self.player, self.opponent])
        self.state = "player_turn" if self.first_player == self.player else "opponent_turn"

    def opponent_attack(self):
        return self.opponent.choose_attack_index(self.player.hand)

    def opponent_defend(self, selected_card_index):
        swap_index = self.opponent.choose_defense_swap(selected_card_index)
        if swap_index is not None:
            self.opponent.hand[selected_card_index], self.opponent.hand[swap_index] = \
                self.opponent.hand[swap_index], self.opponent.hand[selected_card_index]
            return swap_index
        return None

    def game_over(self):
        p1 = self._evaluate_hand(self.player.hand)
        p2 = self._evaluate_hand(self.opponent.hand)

        if (p1[1], p1[2]) > (p2[1], p2[2]):
            self.result = self.player.name
        elif (p1[1], p1[2]) < (p2[1], p2[2]):
            self.result = self.opponent.name
        else:
            self.result = "draw"
