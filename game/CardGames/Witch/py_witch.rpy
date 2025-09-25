init python:
    # ----------------------------
    # USER (side_index = 0) — animations
    # ----------------------------
    def witch_user_discard_pairs_anim(base_delay=0.0, step=0.05):
        """
        Animate user (player 0) discarding all non-Witch pairs.
        Then shuffle hand, update layout, and move to opponent's turn.
        """
        p = card_game.players[0]

        # Track hand before discard
        before = list(p.hand)

        # Discard pairs (excluding Witch)
        p.discard_pairs_excluding_witch(card_game.deck)

        # Track hand after discard to find what was removed
        after = list(p.hand)
        removed = diff_removed(before, after)

        # Animate removed cards to discard pile
        table_animations[:] = []
        for i, card in enumerate(removed):
            src_x, src_y = hand_card_pos(0, card)
            table_animations.append({
                "card": card,
                "src_x": src_x,
                "src_y": src_y,
                "dest_x": DISCARD_X,
                "dest_y": DISCARD_Y,
                "delay": base_delay + i * step,
                "target": "discard",
            })

        # Play animation screen
        show_anim()

        # Shuffle hand and refresh layout after animation
        p.shaffle_hand()
        compute_hand_layout()

        # Move to opponent turn
        card_game.state = "opponent_turn"

    # ----------------------------
    # AI (side_index = 1) — animations
    # ----------------------------
    def witch_ai_discard_pairs_anim(base_delay=0.0, step=0.05):
        """Animate AI pair-discard to the discard pile, then shuffle and continue opponent_turn."""
        p = card_game.players[1]
        before = list(p.hand)
        p.discard_pairs_excluding_witch(card_game.deck)
        after = list(p.hand)
        removed = diff_removed(before, after)

        table_animations[:] = []
        for i, card in enumerate(removed):
            sx, sy = hand_card_pos(1, card)
            table_animations.append({
                "card": card, "src_x": sx, "src_y": sy,
                "dest_x": DISCARD_X, "dest_y": DISCARD_Y,
                "delay": base_delay + i * step, "target": "discard",
            })
        show_anim()

        p.shaffle_hand()

    def witch_ai_take_from_user_anim(index, base_delay=0.0):
        """Animate AI taking a card from User (exchange/drain)."""
        donor = card_game.players[0]
        taker = card_game.players[1]

        sx, sy = hand_card_pos(0, donor.hand[index] if index < len(donor.hand) else donor.hand[-1])
        dx, dy = next_slot_pos(1)

        taken = taker.take_card_from(donor, index=index)
        if hasattr(taker, 'on_after_take'):
            taker.on_after_take(donor, taken)

        table_animations[:] = [{
            "card": taken, "src_x": sx, "src_y": sy,
            "dest_x": dx, "dest_y": dy, "delay": base_delay, "target": "hand1",
        }]
        show_anim()

    # ----------------------------
    # Turns
    # ----------------------------
    def witch_opponent_turn():
        """AI turn logic for Witch game"""
        opponent = card_game.opponent
        deck = card_game.deck
        player = card_game.player

        # 1. AI draws if hand < 6 and deck has cards
        if len(opponent.hand) < 6 and len(deck.cards) > 0:
            print("AI draws cards.")
            witch_ai_draw_to_six_anim()

            # Recalculate layout and discard pairs after drawing
            if opponent.count_pairs_excluding_witch() > 0:
                print("AI discards pairs after draw.")
                compute_hand_layout()
                renpy.pause(1.5)
                witch_ai_discard_pairs_anim()

        # 2. If AI still has discardable pairs (e.g., already had 6 cards), discard now
        elif opponent.count_pairs_excluding_witch() > 0:
            print("AI discards pairs.")
            compute_hand_layout()
            renpy.pause(1.5)
            witch_ai_discard_pairs_anim()

        # 3. Else attempt to exchange a card
        elif opponent.can_exchange_now(deck):
            print("AI attempts to exchange a card.")
            if len(player.hand) == 0:
                print("User has no cards, AI skips exchange.")
            else:
                card_game.state = "wait_choice_opponent"
                donor_idx = card_game.next_player_with_cards(1)
                donor = card_game.players[donor_idx]

                ai_idx = (
                    opponent.choose_exchange_index(donor)
                    if hasattr(opponent, "choose_exchange_index")
                    else renpy.random.randint(0, len(donor.hand) - 1)
                )

                renpy.pause(1.5)
                witch_ai_take_from_user_anim(ai_idx)

                # Discard after exchange
                if opponent.count_pairs_excluding_witch() > 0:
                    print("AI discards pairs after exchange.")
                    compute_hand_layout()
                    renpy.pause(1.5)
                    witch_ai_discard_pairs_anim()

        # 4. End AI turn
        card_game.state = "player_turn"
        compute_hand_layout()