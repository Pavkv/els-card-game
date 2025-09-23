init python:
    # Swap and take animations for Els
    def els_swap_cards_anim(side_index, i, j, base_delay=0.5):
        """Animate swap of two cards in hand — without showing actual opponent cards."""
        hand = card_game.player.hand if side_index == 0 else card_game.opponent.hand
        card_i = hand[i]
        card_j = hand[j]

        # Get original positions BEFORE swap
        src_i = _hand_card_pos(side_index, card_i)
        src_j = _hand_card_pos(side_index, card_j)

        # Use facedown placeholder image for opponent
        img_i = get_card_image(card_i) if side_index == 1 else base_cover_img_src
        img_j = get_card_image(card_j) if side_index == 1 else base_cover_img_src

        # Animate both cards moving to the other's spot
        table_animations[:] = [
            {
                "card": card_i,  # used for ID, not visual
                "src_x": src_i[0], "src_y": src_i[1],
                "dest_x": src_j[0], "dest_y": src_j[1],
                "delay": base_delay,
                "target": "hand" + str(side_index),
                "override_img": img_i,
            },
            {
                "card": card_j,
                "src_x": src_j[0], "src_y": src_j[1],
                "dest_x": src_i[0], "dest_y": src_i[1],
                "delay": base_delay,
                "target": "hand" + str(side_index),
                "override_img": img_j,
            },
        ]

        _show_anim()

        # Now swap the cards in the actual hand
        hand[i], hand[j] = hand[j], hand[i]
        compute_hand_layout()


    # User functions for Els
    def els_user_take_from_opponent_anim(index, base_delay=0.0):
        """Animate user taking a facedown card from AI (exchange/drain)."""
        donor = card_game.opponent
        taker = card_game.player

        # get a visual source: approximate source slot in AI hand
        sx, sy = _hand_card_pos(1, donor.hand[index] if index < len(donor.hand) else donor.hand[-1])
        dx, dy = _next_slot_pos(0)

        # perform the take
        taken = taker.take_card_from(donor, index=index)
        if hasattr(taker, 'on_after_take'):
            taker.on_after_take(donor, taken)

        # animate move to user hand
        table_animations[:] = [{
            "card": taken, "src_x": sx, "src_y": sy,
            "dest_x": dx, "dest_y": dy, "delay": base_delay, "target": "hand0",
        }]
        _show_anim()

    def els_swap_cards_opponent(selected_exchange_card_index_opponent):
        """Handle opponent's card swap during defense phase."""
        card_game.state = "opponent_defend"
        print(card_game.opponent.hand)

        if card_game.turn < 2:
            swap_index = card_game.opponent.choose_defense_swap(selected_exchange_card_index_opponent)
            if swap_index is not None:
                # ❗ Don't swap here — animate first, then swap inside `els_swap_cards_anim`
                els_swap_cards_anim(1, selected_exchange_card_index_opponent, swap_index, base_delay=0.5)
                card_game.turn += 1
                card_game.state = "player_turn"
            else:
                els_user_take_from_opponent_anim(selected_exchange_card_index_opponent)
                selected_exchange_card_index_opponent = -1
                card_game.turn = 0
                card_game.round += 1
                card_game.state = "opponent_turn"
        else:
            els_user_take_from_opponent_anim(selected_exchange_card_index_opponent)
            selected_exchange_card_index_opponent = -1
            card_game.turn = 0
            card_game.round += 1
            card_game.state = "opponent_turn"

        print(card_game.opponent.hand)
        compute_hand_layout()

    # AI functions for Els
    def els_ai_take_from_user_anim(index, base_delay=0.0):
        """Animate AI taking a card from User (exchange/drain)."""
        donor = card_game.player
        taker = card_game.opponent

        sx, sy = _hand_card_pos(0, donor.hand[index] if index < len(donor.hand) else donor.hand[-1])
        dx, dy = _next_slot_pos(1)

        taken = taker.take_card_from(donor, index=index)
        if hasattr(taker, 'on_after_take'):
            taker.on_after_take(donor, taken)

        table_animations[:] = [{
            "card": taken, "src_x": sx, "src_y": sy,
            "dest_x": dx, "dest_y": dy, "delay": base_delay, "target": "hand1",
        }]
        _show_anim()