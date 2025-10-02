init python:
    # ----------------------------
    # Animations
    # ----------------------------
    def discard_pairs_anim(side, base_delay=0.0, step=0.05, on_finish=None):
        """Animate discarding pairs of cards for the given side (0=player, 1=opponent)"""
        p = card_game.player if side == 0 else card_game.opponent
        before = list(p.hand)

        # Actually discard now (only to compute the diff)
        p.discard_pairs_excluding_witch(card_game.deck)

        after = list(p.hand)
        removed = diff_removed(before, after)

        # Restore the hand so animation still works visually
        p.hand = list(before)

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
                "duration": 0.4,
                "target": "discard",
                "override_img": override_img,
            }

            table_animations.append(anim)

        def after_anim():
            p.discard_pairs_excluding_witch(card_game.deck)
            p.shaffle_hand()
            compute_hand_layout()
            if on_finish:
                on_finish()

        show_anim(function=after_anim)

    # ----------------------------
    # User Turn Logic
    # ----------------------------
    def witch_after_draw():
        """Call this after player has pressed the 'draw' button and animation finishes."""
        compute_hand_layout()

        if card_game.player.count_pairs_excluding_witch() > 0:
            card_game.user_turn = "discard_pairs"
        elif card_game.player.can_exchange_now(card_game.deck) and len(card_game.opponent.hand) > 0:
            card_game.user_turn = "exchange"
        else:
            card_game.user_turn = "end_turn"

    def witch_after_discard():
        """Call this after player has pressed 'discard_pairs' and animation finishes."""
        compute_hand_layout()

        if card_game.player.can_exchange_now(card_game.deck) and len(card_game.opponent.hand) > 0:
            card_game.user_turn = "exchange"
        else:
            card_game.user_turn = "end_turn"

    def witch_after_exchange():
        """Call this after player has selected and taken a card from opponent."""
        compute_hand_layout()

        if card_game.player.count_pairs_excluding_witch() > 0:
            card_game.user_turn = "discard_pairs"
        else:
            card_game.user_turn = "end_turn"

    def witch_end_player_turn():
        """Call this when player presses 'end_turn' button or finishes last action."""
        card_game.state = "opponent_turn"
        compute_hand_layout()

    # ----------------------------
    # Opponent Turn Logic
    # ----------------------------
    def witch_opponent_turn():
        """AI turn logic for Witch game"""
        opponent = card_game.opponent
        deck = card_game.deck
        player = card_game.player

        def end_turn():
            print("AI ends turn.")
            card_game.state = "player_turn"
            card_game.player_turn_start()
            compute_hand_layout()

        def maybe_discard_after_exchange():
            if opponent.count_pairs_excluding_witch() > 0:
                print("AI discards pairs after exchange.")
                discard_pairs_anim(side=1, on_finish=end_turn)
            else:
                end_turn()

        def maybe_exchange():
            if opponent.can_exchange_now(deck):
                print("AI attempts to exchange a card.")
                if len(player.hand) == 0:
                    print("User has no cards, AI skips exchange.")
                    end_turn()
                else:
                    card_game.state = "wait_choice_opponent"
                    donor = card_game.player

                    index = (
                        opponent.choose_exchange_index(donor)
                        if hasattr(opponent, "choose_exchange_index")
                        else renpy.random.randint(0, len(donor.hand) - 1)
                    )

                    take_card_anim(from_side=0, to_side=1, index=index, on_finish=maybe_discard_after_exchange)
            else:
                end_turn()

        def maybe_discard_after_draw():
            if opponent.count_pairs_excluding_witch() > 0:
                print("AI discards pairs after draw.")
                discard_pairs_anim(side=1, on_finish=maybe_exchange)
            else:
                maybe_exchange()

        def maybe_discard_before_exchange():
            if opponent.count_pairs_excluding_witch() > 0:
                print("AI discards pairs before exchange.")
                discard_pairs_anim(side=1, on_finish=maybe_exchange)
            else:
                maybe_exchange()

        def after_draw():
            compute_hand_layout()
            maybe_discard_after_draw()

        if len(opponent.hand) < 6 and len(deck.cards) > 0:
            print("AI draws cards.")
            draw_anim(side=1, target_count=6, on_finish=after_draw)
        else:
            maybe_discard_before_exchange()
