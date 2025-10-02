from collections import OrderedDict
from Card import Card

class Table:
    def __init__(self):
        self.table = OrderedDict()  # {attack_card: [is_beaten: bool, defending_card: Card or None]}
        self.ranks = set()

    def __str__(self):
        return "Table: {}".format(", ".join(str(card) for card in self.table))

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.table)

    def keys(self):
        return self.table.keys()

    def values(self):
        return [v[1] for v in self.table.values()]

    def can_append(self, card):
        return not self.table or card.rank in self.ranks

    def append(self, card):
        if not self.can_append(card):
            return False
        self.table[card] = [False, None]
        self.ranks.add(card.rank)
        return True

    def beat(self, attack_card, defend_card):
        if attack_card in self.table:
            self.table[attack_card] = [True, defend_card]
            self.ranks.add(defend_card.rank)

    def can_beat(self, defender_hand, trump_suit):
        for attack_card, (is_beaten, _) in self.table.items():
            if is_beaten:
                continue
            if not any(Card.beats(def_card, attack_card, trump_suit) for def_card in defender_hand):
                return False
        return True

    def num_beaten(self):
        return sum(1 for status in self.table.values() if status[0])

    def num_unbeaten(self):
        return sum(1 for status in self.table.values() if not status[0])

    def first_unbeaten(self):
        for (i, attack_card, (is_beaten, _)) in enumerate(self.table.items()):
            if not is_beaten:
                return i, attack_card
        return None, None

    def beaten(self):
        return all(status[0] for status in self.table.values()) if self.table else False

    def clear(self):
        self.table.clear()
        self.ranks.clear()
