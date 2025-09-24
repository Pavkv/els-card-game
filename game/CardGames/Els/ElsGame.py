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
        self.round = 1
        self.turn = 1
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

        rank_counts = {}
        suit_counts = {}
        for r in ranks:
            rank_counts[r] = rank_counts.get(r, 0) + 1
        for s in suits:
            suit_counts[s] = suit_counts.get(s, 0) + 1

        rank_values = sorted([rank_order[r] for r in ranks], reverse=True)

        def is_straight(values):
            values = sorted(list(set(values)), reverse=True)
            for i in range(len(values) - 4):
                window = values[i:i + 5]
                if window == list(range(window[0], window[0] - 5, -1)):
                    return True, window
            return False, []

        flush_suit = None
        for suit in suit_counts:
            if suit_counts[suit] >= 5:
                flush_suit = suit
                break

        flush_cards = []
        if flush_suit:
            flush_cards = [card for card in cards if card.suit == flush_suit]
            flush_cards.sort(key=lambda c: rank_order[c.rank], reverse=True)

        is_straight_all, straight_vals = is_straight(rank_values)
        is_straight_flush, straight_flush_vals = False, []
        if flush_suit:
            flush_flush_values = [rank_order[c.rank] for c in flush_cards]
            is_straight_flush, straight_flush_vals = is_straight(flush_flush_values)

        # Frequency map
        freq_map = {}
        for rank in rank_counts:
            count = rank_counts[rank]
            val = rank_order[rank]
            if count not in freq_map:
                freq_map[count] = []
            freq_map[count].append(val)

        for freq in freq_map:
            freq_map[freq].sort(reverse=True)

        def hand(name, rank, tiebreakers, combo_cards):
            # Get indexes in original hand
            indices = [cards.index(card) for card in combo_cards]
            return name, rank, tiebreakers, indices

        if is_straight_flush and max(straight_flush_vals) == rank_order['A']:
            combo_cards = []
            for v in straight_flush_vals:
                for c in flush_cards:
                    if rank_order[c.rank] == v and c not in combo_cards:
                        combo_cards.append(c)
                        break
            return hand("Роял-флеш", 10, [rank_order['A']], combo_cards)

        elif is_straight_flush:
            combo_cards = []
            for v in straight_flush_vals:
                for c in flush_cards:
                    if rank_order[c.rank] == v and c not in combo_cards:
                        combo_cards.append(c)
                        break
            return hand("Стрит-флэш", 9, straight_flush_vals, combo_cards)

        elif 4 in freq_map:
            four = freq_map[4][0]
            kicker = [v for v in rank_values if v != four][0]
            combo_cards = [c for c in cards if rank_order[c.rank] == four][:4]
            combo_cards += [c for c in cards if rank_order[c.rank] == kicker][:1]
            return hand("Каре", 8, [four, kicker], combo_cards)

        elif 3 in freq_map and 2 in freq_map:
            three = freq_map[3][0]
            two = freq_map[2][0]
            combo_cards = [c for c in cards if rank_order[c.rank] == three][:3]
            combo_cards += [c for c in cards if rank_order[c.rank] == two][:2]
            return hand("Фулл-хаус", 7, [three, two], combo_cards)

        elif flush_suit:
            combo_cards = flush_cards[:5]
            values = [rank_order[c.rank] for c in combo_cards]
            return hand("Флэш", 6, values, combo_cards)

        elif is_straight_all:
            combo_cards = []
            for v in straight_vals:
                for c in sorted(cards, key=lambda c: rank_order[c.rank], reverse=True):
                    if rank_order[c.rank] == v and c not in combo_cards:
                        combo_cards.append(c)
                        break
            return hand("Стрит", 5, straight_vals, combo_cards)

        elif 3 in freq_map:
            three = freq_map[3][0]
            kickers = [v for v in rank_values if v != three][:2]
            combo_cards = [c for c in cards if rank_order[c.rank] == three][:3]
            combo_cards += [c for c in cards if rank_order[c.rank] in kickers][:2]
            return hand("Тройка", 4, [three] + kickers, combo_cards)

        elif 2 in freq_map and len(freq_map[2]) >= 2:
            pair1, pair2 = freq_map[2][:2]
            kicker = [v for v in rank_values if v not in (pair1, pair2)][0]
            combo_cards = []
            combo_cards += [c for c in cards if rank_order[c.rank] == pair1][:2]
            combo_cards += [c for c in cards if rank_order[c.rank] == pair2][:2]
            combo_cards += [c for c in cards if rank_order[c.rank] == kicker][:1]
            return hand("Две Пары", 3, [pair1, pair2, kicker], combo_cards)

        elif 2 in freq_map:
            pair = freq_map[2][0]
            kickers = [v for v in rank_values if v != pair][:3]
            combo_cards = [c for c in cards if rank_order[c.rank] == pair][:2]
            combo_cards += [c for c in cards if rank_order[c.rank] in kickers][:3]
            return hand("Пара", 2, [pair] + kickers, combo_cards)

        else:
            combo_cards = sorted(cards, key=lambda c: rank_order[c.rank], reverse=True)[:5]
            values = [rank_order[c.rank] for c in combo_cards]
            return hand("Старшая Карта", 1, values, combo_cards)

    # ---------- externals ----------
    def start_game(self):
        self._deal_each()
        self.first_player = random.choice([self.player, self.opponent])
        self.state = "player_turn" if self.first_player == self.player else "opponent_turn"

    def opponent_attack(self):
        return self.opponent.choose_attack_index(self.player.hand)

    def game_over(self):
        p1 = self._evaluate_hand(self.player.hand)
        p2 = self._evaluate_hand(self.opponent.hand)

        if (p1[1], p1[2]) > (p2[1], p2[2]):
            self.result = self.player.name
        elif (p1[1], p1[2]) < (p2[1], p2[2]):
            self.result = self.opponent.name
        else:
            self.result = "draw"

        return self.result, p1, p2