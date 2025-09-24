init python:
    # Swap and take animations for Els
    def els_swap_cards_anim(side_index, i, j, base_delay=0.5, anim_duration=1.0):
        """Smooth animation: cards slide into each other's position in-place."""

        hand = card_game.player.hand if side_index == 0 else card_game.opponent.hand
        card_i = hand[i]
        card_j = hand[j]

        # Position before swap
        src_i = _hand_card_pos(side_index, card_i)
        src_j = _hand_card_pos(side_index, card_j)

        # Use appropriate images
        img_i = get_card_image(card_i) if side_index == 0 else base_cover_img_src
        img_j = get_card_image(card_j) if side_index == 0 else base_cover_img_src

        # Prepare animation entries
        table_animations[:] = [
            {
                "card": card_i,
                "src_x": src_i[0], "src_y": src_i[1],
                "dest_x": src_j[0], "dest_y": src_j[1],
                "delay": base_delay,
                "duration": anim_duration,
                "target": "hand" + str(side_index),
                "override_img": img_i,
            },
            {
                "card": card_j,
                "src_x": src_j[0], "src_y": src_j[1],
                "dest_x": src_i[0], "dest_y": src_i[1],
                "delay": base_delay,
                "duration": anim_duration,
                "target": "hand" + str(side_index),
                "override_img": img_j,
            },
        ]

        _show_anim()

        # Swap cards in data
        hand[i], hand[j] = hand[j], hand[i]
        compute_hand_layout()

    # User functions for Els
    def els_user_take_from_opponent_anim(index, base_delay=0.1):
        """Animate user taking a facedown card from AI (exchange/drain)."""
        global selected_exchange_card_index_opponent
        donor = card_game.opponent
        taker = card_game.player

        # get a visual source: approximate source slot in AI hand
        src_card = donor.hand[index] if index < len(donor.hand) else donor.hand[-1]
        sx, sy = _hand_card_pos(1, src_card)
        dx, dy = _next_slot_pos(0)

        # perform the take
        taken = taker.take_card_from(donor, index=index)

        if hasattr(taker, 'on_after_take'):
            taker.on_after_take(donor, taken)

        # Temporarily remove card from player's hand so it's not visible during animation
        taker.hand.remove(taken)
        compute_hand_layout()

        # animate move to user hand
        table_animations[:] = [{
            "card": taken,
            "src_x": sx,
            "src_y": sy,
            "dest_x": dx,
            "dest_y": dy,
            "delay": base_delay,
            "target": "hand0",
            "override_img": base_cover_img_src,
            "duration": 0.4,
        }]
        _show_anim()

        taker.hand.append(taken)
        compute_hand_layout()
        card_game.turn = 1
        card_game.round += 1
        selected_exchange_card_index_opponent = -1
        card_game.state = "opponent_turn"

    def els_swap_cards_opponent():
        """Handle opponent's card swap during defense phase."""
        global selected_exchange_card_index_opponent, hovered_card_index_exchange
        card_game.state = "opponent_defend"
        print(card_game.opponent.hand)

        if card_game.turn <= 2:
            swap_index = card_game.opponent.choose_defense_swap(selected_exchange_card_index_opponent)
            if swap_index is not None:
                index = selected_exchange_card_index_opponent
                selected_exchange_card_index_opponent = -1
                hovered_card_index_exchange = -1

                els_swap_cards_anim(1, index, swap_index)

                card_game.turn += 1
                card_game.state = "player_turn"
            else:
                els_user_take_from_opponent_anim(selected_exchange_card_index_opponent)
                selected_exchange_card_index_opponent = -1
                hovered_card_index_exchange = -1
        else:
            els_user_take_from_opponent_anim(selected_exchange_card_index_opponent)
            selected_exchange_card_index_opponent = -1
            hovered_card_index_exchange = -1

        print(card_game.opponent.hand)
        compute_hand_layout()

    # AI functions for Els
    def els_ai_take_from_user_anim(index, base_delay=0.1):
        global selected_exchange_card_index_player

        """Animate AI taking a card from User (exchange/drain)."""
        donor = card_game.player
        taker = card_game.opponent

        # Visual source position in player hand
        src_card = donor.hand[index] if index < len(donor.hand) else donor.hand[-1]
        sx, sy = _hand_card_pos(0, src_card)
        dx, dy = _next_slot_pos(1)

        # Perform the take
        taken = taker.take_card_from(donor, index=index)

        if hasattr(taker, 'on_after_take'):
            taker.on_after_take(donor, taken)

        # Temporarily remove card from opponent hand to hide it during animation
        taker.hand.remove(taken)
        compute_hand_layout()

        # Animate movement
        table_animations[:] = [{
            "card": taken,
            "src_x": sx,
            "src_y": sy,
            "dest_x": dx,
            "dest_y": dy,
            "delay": base_delay,
            "duration": 0.4,
            "target": "hand1",
            "override_img": get_card_image(taken),  # You can use `base_cover_img_src` if you want it hidden
        }]
        _show_anim()

        taker.hand.append(taken)
        compute_hand_layout()
        card_game.turn = 1
        card_game.round += 1
        selected_exchange_card_index_player = -1
        card_game.state = "player_turn"

    def els_swap_cards_player(selected_card_index):
        """Handle player's card swap during defense phase."""
        global selected_exchange_card_index_player, hovered_card_index
        print(card_game.player.hand)

        # Save then clear selection/hover before animating
        index = selected_exchange_card_index_player
        selected_exchange_card_index_player = -1
        hovered_card_index = -1

        els_swap_cards_anim(0, selected_card_index, index)

        card_game.turn += 1
        card_game.state = "opponent_turn"

        print(card_game.player.hand)
        compute_hand_layout()

    def results_els():
        global result_combination_player, result_combination_indexes_player, result_combination_opponent, result_combination_indexes_opponent, selected_exchange_card_index_opponent, selected_exchange_card_index_player
        selected_exchange_card_index_opponent = -1
        selected_exchange_card_index_player = -1
        renpy.pause(1.0)
        results = card_game.game_over()
        card_game.result = results[0]
        result_combination_player = results[1][0]
        result_combination_indexes_player = results[1][3]
        result_combination_opponent = results[2][0]
        result_combination_indexes_opponent = results[2][3]
        print("Game Over: ", card_game.result)
        card_game.state = "results"