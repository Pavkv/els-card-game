init python:
    import random

    from CardGames.Classes.Card import Card
    from CardGames.Durak.DurakGame import DurakGame
    from CardGames.G21.Game21 import Game21
    from CardGames.Witch.WitchGame import WitchGame
    from game.CardGames.Els.ElsGame import ElsGame

    # Global variables
    CARD_WIDTH, CARD_HEIGHT, CARD_SPACING = 157, 237, 118
    suits = {'C': 'uvao', 'D': '2ch', 'H': 'ussr', 'S': 'utan'}
    ranks = {'6': '6', '7': '7', '8': '8', '9': '9', '10': '10', 'J': '11', 'Q': '12', 'K': '13', 'A': '1'} # '2': '2', '3': '3', '4': '4', '5': '5',

    # ----------------------------
    # Game Setup Functions
    # ----------------------------
    def get_card_image(card):
        """Returns the image path for a card based on its rank and suit."""
        return base_card_img_src + "/{}_{}.png".format(ranks[card.rank], suits[card.suit])

    def get_opponent_avatar_base():
        """
        Returns a path/displayable for the opponent avatar.
        Supports dict (prefers 'body') or string; falls back to placeholder.
        """
        placeholder = "images/cards/avatars/empty_avatar.png"
        try:
            opp = getattr(store, "card_game").opponent
            av = getattr(opp, "avatar", None)

            # dict: prefer 'body'
            if isinstance(av, dict):
                body = av.get("body")
                if body:
                    return body
                # pick first string in dict if no 'body'
                for v in av.itervalues():
                    if isinstance(v, basestring):
                        return v
                return placeholder

            # string path
            if isinstance(av, basestring):
                return av
        except Exception:
            pass
        return placeholder

    def opponent_avatar_displayable(size=(150, 150), pad=6, top_pad=6):
        """
        Returns the avatar scaled to fit inside `size` with side padding
        and only top padding (no bottom padding).
        """
        base = get_opponent_avatar_base()

        inner_w = max(1, size[0] - pad * 2)
        inner_h = max(1, size[1] - top_pad)

        avatar = Transform(base, xysize=(inner_w, inner_h))

        box = Fixed(
            xmaximum=size[0], ymaximum=size[1],
            xminimum=size[0], yminimum=size[1]
        )

        positioned_avatar = Transform(avatar, xpos=pad, ypos=top_pad)

        box.add(positioned_avatar)
        return box

    def compute_hand_layout():
        """Computes the layout for player and opponent hands based on the number of cards."""
        global player_card_layout, opponent_card_layout
        def layout(total, y, max_right_x):
            total_width = CARD_WIDTH + (total - 1) * CARD_SPACING
            max_hand_width = max_right_x - 20
            if total_width <= max_hand_width:
                spacing = CARD_SPACING
                start_x = max((1920 - total_width) // 2, 20)
            else:
                spacing = (max_hand_width - CARD_WIDTH) // max(total - 1, 1)
                start_x = 20
            return [{"x": start_x + i * spacing, "y": y} for i in range(total)]
        player_card_layout = layout(len(card_game.player.hand), 825, 1700)
        opponent_card_layout = layout(len(card_game.opponent.hand), 20, 1680)

    def is_card_animating(card):
        for anim in table_animations:
            if anim["card"] == card:
                return True
        return False

    def handle_card_action(card_game, index):
        if isinstance(card_game, DurakGame):
            return Function(durak_handle_card_click, index)
        elif isinstance(card_game, ElsGame) and card_game.state == "player_defend":
            return Function(lambda: els_swap_cards_player(index))
        return Return()

    # ----------------------------
    # Position Helpers
    # ----------------------------
    def diff_removed(before, after):
        """Return list of (index, card) tuples for removed cards."""
        removed = []
        after_set = set(after)
        for i, c in enumerate(before):
            if c not in after_set:
                removed.append((i, c))
        return removed

    def hand_card_pos(side_index, card, override_index=None):
        """Return the layout position (x, y) of the given card in hand layout."""
        layout = player_card_layout if side_index == 0 else opponent_card_layout
        hand = card_game.player.hand if side_index == 0 else card_game.opponent.hand

        if override_index is not None:
            idx = override_index
        else:
            try:
                idx = hand.index(card)
            except ValueError:
                idx = 0  # fallback index

        return layout[idx]["x"], layout[idx]["y"]

    def next_slot_pos(side_index):
        """Position where the next card would visually land in the hand."""
        hand = card_game.player.hand if side_index == 0 else card_game.opponent.hand
        idx = len(hand)
        return (HAND0_X + idx * HAND_SPACING, HAND0_Y) if side_index == 0 else (HAND1_X + idx * HAND_SPACING, HAND1_Y)

    def show_anim():
        renpy.show_screen("table_card_animation")

    # ----------------------------
    # Game Start Function
    # ----------------------------
    def start_card_game(game_class, game_name, num_of_cards=6, game_args=(), game_kwargs={}):
        """
        Initializes any card game with dealing animation setup.

        Arguments:
        - game_class: the class of the game (e.g., WitchGame)
        - game_name: string name of the game (e.g., "witch")
        - base_cover_src: base path to card back image
        - player_name, opponent_name: names of the players
        - opponent_avatar: avatar image for the opponent
        - biased_draw: optional bias config
        """
        global card_game, player_name, opponent_name, biased_draw, card_game_name
        global base_cover_img_src, base_card_img_src, card_game_avatar
        global dealt_cards, is_dealing, deal_cards

        card_game = game_class(player_name, opponent_name, biased_draw, *game_args, **game_kwargs)
        card_game_name = game_name
        base_cover_img_src = base_card_img_src + "/cover.png"
        card_game.opponent.avatar = card_game_avatar

        card_game.start_game(num_of_cards)
        compute_hand_layout()

        dealt_cards = []
        is_dealing = True
        deal_cards = True

        delay = 0.0
        for i in range(len(card_game.player.hand)):
            dealt_cards.append({
                "owner": "player",
                "index": i,
                "delay": delay
            })
            delay += 0.1

        for i in range(len(card_game.opponent.hand)):
            dealt_cards.append({
                "owner": "opponent",
                "index": i,
                "delay": delay
            })
            delay += 0.1

        renpy.show_screen("card_game_base_ui")

        renpy.jump(game_name + "_game_loop")

    # ----------------------------
    # In Game Functions
    # ----------------------------
    def draw_anim(side, target_count=6, step_delay=0.05):
        """
        Animate drawing cards for the given side (0 = player, 1 = opponent)
        until the hand has `target_count` cards or the deck is empty.
        """
        d = 0.0
        table_animations[:] = []

        player = card_game.player if side == 0 else card_game.opponent
        bias_key = "player" if side == 0 else "opponent"
        target = "hand{}".format(side)

        while len(player.hand) < target_count and not card_game.deck.is_empty():
            dest_x, dest_y = next_slot_pos(side)

            player.draw_from_deck(
                card_game.deck,
                target_count,
                sort_hand=False,
                good_prob=card_game.bias[bias_key]
            )

            card = player.hand[-1]

            override_img = get_card_image(card) if side == 0 else base_cover_img_src

            table_animations.append({
                "card": card,
                "src_x": DECK_X,
                "src_y": DECK_Y,
                "dest_x": dest_x,
                "dest_y": dest_y,
                "delay": d,
                "target": target,
                "override_img": override_img,
            })

            d += step_delay

        if table_animations:
            show_anim()

        compute_hand_layout()

    def take_card_anim(
        from_side,
        to_side,
        index,
        base_delay=0.1,
        duration=0.4
    ):
        """
        Animate a card being taken from one player to another.

        Parameters:
            from_side (int): 0 = player, 1 = opponent (donor)
            to_side (int): 0 = player, 1 = opponent (taker)
            index (int): index of the card to take from donor
            base_delay (float): delay before animation
            duration (float): animation duration
            override_img (str or None): override image for animation (e.g. face-down card)
        """
        donor = card_game.player if from_side == 0 else card_game.opponent
        taker = card_game.player if to_side == 0 else card_game.opponent

        # Get card and its visual source position
        src_card = donor.hand[index] if index < len(donor.hand) else donor.hand[-1]
        sx, sy = hand_card_pos(from_side, src_card)
        dx, dy = next_slot_pos(to_side)

        # Perform the take
        taken = taker.take_card_from(donor, index=index)

        if hasattr(taker, 'on_after_take'):
            taker.on_after_take(donor, taken)

        # Temporarily remove card from taker's hand so it doesn't flash early
        taker.hand.remove(taken)
        compute_hand_layout()

        # Use appropriate image for animation
        override_img = get_card_image(taken) if to_side == 1 else base_cover_img_src

        table_animations[:] = [{
            "card": taken,
            "src_x": sx,
            "src_y": sy,
            "dest_x": dx,
            "dest_y": dy,
            "delay": base_delay,
            "duration": duration,
            "target": "hand{}".format(to_side),
            "override_img": override_img,
        }]
        show_anim()

        # Return the card to taker's hand
        taker.hand.append(taken)
        compute_hand_layout()

    # ----------------------------
    # Reset Game Function
    # ----------------------------
    def reset_card_game():
        s = store

        # base
        s.in_game = True
        s.card_game = None
        s.player_name = None
        s.base_card_img_src = None
        s.base_cover_img_src = None
        s.cards_bg = None
        s.hovered_card_index = -1
        s.dealt_cards = []
        s.is_dealing = False
        s.draw_animations = []
        s.is_drawing = False
        s.table_animations = []
        s.is_table_animating = False
        s.player_card_layout = []
        s.opponent_card_layout = []
        s.biased_draw = None
        s.hovered_card_index_exchange = -1
        s.selected_exchange_card_index = -1

        # els-specific
        s.result_combination_player = None
        s.result_combination_indexes_player = set()
        s.result_combination_opponent = None
        s.result_combination_indexes_opponent = set()

        # durak-specific
        s.selected_card = None
        s.selected_attack_card = None
        s.attack_target = None
        s.selected_attack_card_indexes = set()
        s.selected_card_indexes = set()
        s.confirm_attack = False
        s.confirm_take = False

        # game 21-specific
        s.g21_card_num = 1
        s.g21_aces_low = False

        # witch-specific
        s.made_turn = False