init python:
    # ----------------------------
    # Animations
    # ----------------------------
    def discard_pairs_anim(side, base_delay=0.0, step=0.2):
        """Animate discarding pairs (e.g. in Witch or other games)."""
        p = card_game.player if side == 0 else card_game.opponent
        before = list(p.hand)

        p.discard_pairs_excluding_witch(card_game.deck)

        after = list(p.hand)
        removed = diff_removed(before, after)  # returns (index, card) tuples

        table_animations[:] = []
        for i, (idx, card) in enumerate(removed):
            sx, sy = hand_card_pos(side, card, override_index=idx)

            override_img = get_card_image(card) if side == 0 else base_cover_img_src

            anim = {
                "card": card,
                "src_x": sx,
                "src_y": sy,
                "dest_x": DISCARD_X,
                "dest_y": DISCARD_Y,
                "delay": base_delay + i * step,
                "target": "discard",
                "override_img": override_img,
            }

            table_animations.append(anim)

        show_anim()
        p.shaffle_hand()
        compute_hand_layout()

    # ----------------------------
    # Turns
    # ----------------------------
    def witch_player_turn():
        """AI turn logic for Witch game"""
        global selected_exchange_card_index_opponent, hovered_card_index_exchange, made_turn

        take_card_anim(1, 0, selected_exchange_card_index_opponent)
        selected_exchange_card_index_opponent = -1
        hovered_card_index_exchange = -1
        compute_hand_layout()

        if  card_game.player.count_pairs_excluding_witch() > 0:
            card_game.state = "player_turn"
            made_turn = True
        else:
            card_game.state = "opponent_turn"

    def witch_opponent_turn():
        """AI turn logic for Witch game"""
        opponent = card_game.opponent
        deck = card_game.deck
        player = card_game.player

        # 1. AI draws if hand < 6 and deck has cards
        if len(opponent.hand) < 6 and len(deck.cards) > 0:
            print("AI draws cards.")
            draw_anim(1, 6)

            # Recalculate layout and discard pairs after drawing
            if opponent.count_pairs_excluding_witch() > 0:
                print("AI discards pairs after draw.")
                compute_hand_layout()
                renpy.pause(1.5)
                discard_pairs_anim(1)

        # 2. If AI has pairs, discard them
        if opponent.count_pairs_excluding_witch() > 0:
            print("AI discards pairs before exchange.")
            compute_hand_layout()
            renpy.pause(1.5)
            discard_pairs_anim(1)

        # 3. Else attempt to exchange a card
        if opponent.can_exchange_now(deck):
            print("AI attempts to exchange a card.")
            if len(player.hand) == 0:
                print("User has no cards, AI skips exchange.")
            else:
                card_game.state = "wait_choice_opponent"
                donor = card_game.player

                index = (
                    opponent.choose_exchange_index(donor)
                    if hasattr(opponent, "choose_exchange_index")
                    else renpy.random.randint(0, len(donor.hand) - 1)
                )

                renpy.pause(1.5)
                take_card_anim(0, 1, index)

                # Discard after exchange
                if opponent.count_pairs_excluding_witch() > 0:
                    print("AI discards pairs after exchange.")
                    compute_hand_layout()
                    renpy.pause(1.5)
                    discard_pairs_anim(1)

        # 4. End AI turn
        card_game.state = "player_turn"
        compute_hand_layout()