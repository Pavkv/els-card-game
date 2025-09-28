init python:
     # --------------------
     # Durak Animations
     # --------------------
    def animate_table_cards(card_game, step_delay=0.2):
        """
        Animate cards being cleared from the table.
        If the table is NOT beaten, cards go to the receiving player's hand.
        If beaten, all cards go to the discard pile.
        """
        table_animations[:] = []
        delay = 0.0

        is_beaten = card_game.table.beaten()
        receiver = (
            card_game.player
            if card_game.current_turn != card_game.player
            else card_game.opponent
        )

        for i, (atk, (beaten, def_card)) in enumerate(card_game.table.table.items()):
            src_x = 350 + i * 200
            src_y = 375
            cards = list(filter(None, [atk, def_card]))

            for card in cards:
                anim = {
                    "card": card,
                    "src_x": src_x,
                    "src_y": src_y if card == atk else src_y + 120,
                    "delay": delay,
                }

                if is_beaten:
                    anim.update({
                        "dest_x": 1600,
                        "dest_y": 350,
                        "target": "discard",
                    })
                else:
                    anim.update({
                        "dest_x": 700,
                        "dest_y": 825 if receiver == card_game.player else 20,
                        "target": "hand",
                    })

                table_animations.append(anim)
                delay += step_delay

        if table_animations:
            show_anim()

    def play_card_anim(card, side, slot_index=0, is_defense=False, delay=0.0):
        """
        Animate playing a card from the player's or opponent's hand onto the table.

        Arguments:
        - card: the Card object to animate
        - side: 0 for player, 1 for opponent
        - slot_index: index on table (0 for first attack, 1 for next, etc.)
        - is_defense: if True, card is placed below the attack card
        - delay: optional delay before animation starts
        """
        table_animations[:] = []

        # Hand source position
        src_x, src_y = hand_card_pos(side, card)

        # Table destination position
        base_x = 350 + slot_index * 200
        base_y = 375
        dest_x = base_x
        dest_y = base_y + 120 if is_defense else base_y

        # Choose card image override
        override_img = get_card_image(card) if side == 0 else base_cover_img_src

        table_animations.append({
            "card": card,
            "src_x": src_x,
            "src_y": src_y,
            "dest_x": dest_x,
            "dest_y": dest_y,
            "delay": delay,
            "target": "table",
            "override_img": override_img,
        })

        show_anim()
        compute_hand_layout()

    # --------------------
    # Player Functions
    # --------------------
    def durak_handle_card_click(index):
        """Handles card click events for player actions."""
        global confirm_attack, selected_attack_card_indexes, selected_attack_card

        card = card_game.player.hand[index]
        print("Card clicked:", card)

        # Player attack phase
        if card_game.state == "player_turn":
            if index in selected_attack_card_indexes:
                selected_attack_card_indexes.remove(index)
                print("Unselected:", card)
            else:
                # Allow selecting if first or same rank as already selected
                allowed_ranks = {card_game.player.hand[i].rank for i in selected_attack_card_indexes}
                if not selected_attack_card_indexes or card.rank in allowed_ranks:
                    selected_attack_card_indexes.add(index)
                    print("Selected:", card)

            confirm_attack = len(selected_attack_card_indexes) > 0

        # Player defend phase
        elif card_game.state == "player_defend" and selected_attack_card:
            if card_game.defend_card(card, selected_attack_card):
                print("Player defended against {} with {}".format(selected_attack_card, card))

                # Animate defense card going to table
                table_size = len(card_game.table)
                attack_slot_index = next((i for i, (atk, _) in enumerate(card_game.table.table.items()) if atk == selected_attack_card), table_size - 1)

                play_card_anim(
                    card=card,
                    side=0,
                    slot_index=attack_slot_index,
                    is_defense=True,
                    delay=0.0
                )
                show_anim()

                selected_attack_card = None
                card_game.state = "opponent_turn"
            else:
                print("Invalid defense with:", card)
                selected_attack_card = None

    def durak_confirm_selected_attack():
        """Confirms all selected attack cards and animates them from hand to table."""
        global confirm_attack, selected_attack_card_indexes

        if confirm_attack and selected_attack_card_indexes:
            indexes = sorted(selected_attack_card_indexes)
            cards = [card_game.player.hand[i] for i in indexes]

            if card_game.attack_cards(cards):
                print("Player attacked with: " + ', '.join(str(c) for c in cards))

                # Animate each card moving to table
                table_animations[:] = []
                for i, card in enumerate(cards):
                    play_card_anim(
                        card=card,
                        side=0,
                        slot_index=len(card_game.table) - len(cards) + i,
                        is_defense=False,
                        delay=i * 0.1
                    )

                show_anim()

                # Clear selection and proceed to opponent turn
                selected_attack_card_indexes.clear()
                confirm_attack = False
                card_game.state = "opponent_defend"

            else:
                print("Invalid attack. Resetting selection.")
                selected_attack_card_indexes.clear()
                confirm_attack = False

    # --------------------
    # Opponent Functions
    # --------------------
    def durak_opponent_turn():
        """Handles opponent's attack selection logic."""
        global confirm_take

        if card_game.can_attack(card_game.opponent):
            attack_success = card_game.opponent_attack()
            if attack_success:
                print("AI attacked successfully with:", list(card_game.table.table.keys()))
                renpy.pause(1.5)
                card_game.state = "player_defend"

                table_size = len(card_game.table)
                delay = 0.0
                for i, (card, _) in enumerate(card_game.table.table.items()):
                    play_card_anim(
                        card=card,
                        side=1,
                        slot_index=i,
                        is_defense=False,
                        delay=delay
                    )
                    delay += 0.05

                show_anim()

            else:
                print("AI attempted to attack but failed unexpectedly.")
                card_game.state = "end_turn"

        else:

            if not card_game.table.beaten() and not confirm_take:
                print("AI skipped attack; player must still defend or take.")
                card_game.state = "player_defend"

            else:
                print("AI cannot attack and table is beaten. Ending turn.")
                confirm_take = False
                card_game.state = "end_turn"

    def durak_opponent_defend():
        """Handles the opponent's defense logic against player attack."""
        defend_success = card_game.opponent_defend()

        if defend_success:
            print("AI defended successfully.")
            # Animate defense (card placed on top of attack)
            delay = 0.0
            for i, (atk, (beaten, def_card)) in enumerate(card_game.table.table.items()):
                if beaten and def_card:
                    play_card_anim(
                        card=def_card,
                        side=1,  # opponent
                        slot_index=i,
                        is_defense=True,
                        delay=delay
                    )
                    delay += 0.1
            show_anim()

        else:
            print("AI could not defend. Player wins this round.")

        card_game.state = "player_turn"

    # --------------------
    # End Turn Logic
    # --------------------
    def durak_end_turn():
        global confirm_take  # Ensure this resets the global flag

        # AI Throw-ins if it was the AI's turn and player still can be attacked
        if card_game.current_turn == card_game.opponent and card_game.can_attack(card_game.opponent):
            print("AI adding throw-ins.")
            card_game.throw_ins()

        print("Table before ending turn:", card_game.table)
        print("Player hand before ending turn:", card_game.player.hand)
        print("Opponent hand before ending turn:", card_game.opponent.hand)

        # Animate cards moving off the table
        animate_table_cards(card_game)

        # Check for special two sixes attack
        attack_cards = [atk for atk, (_b, _d) in card_game.table.table.items()]
        print("Attack cards:", attack_cards)

        last_attack_two_sixes = False
        if len(attack_cards) == 2:
            last_attack_two_sixes = all(
                getattr(c, "rank", None) in ("6", 6) for c in attack_cards
            )

        lost_to_two_sixes = (
            card_game.current_turn == card_game.opponent
            and last_attack_two_sixes
            and card_game.deck.is_empty()
        )

        # Clear table: either take or discard
        card_game.take_or_discard_cards()
        card_game.opponent.remember_table(card_game.table)
        card_game.opponent.remember_discard(card_game.deck.discard)

        # Clear table
        card_game.table.clear()

        # Draw cards to 6 for both players
        draw_anim(0, 6 - len(card_game.player.hand))
        draw_anim(1, 6 - len(card_game.opponent.hand))

        # Check for game over conditions
        card_game.check_endgame()

        # Set next state
        card_game.state = "player_turn" if card_game.current_turn == card_game.player else "opponent_turn"

        print("Discard pile:", card_game.deck.discard)
        print("Player hand after turn:", card_game.player.hand)
        print("Opponent hand after turn:", card_game.opponent.hand)

        # Check if game has ended
        if card_game.result:
            card_game.state = "result"
            return

        print("Player hand after drawing:", card_game.player.hand)
        print("Opponent hand after drawing:", card_game.opponent.hand)

        confirm_take = False
