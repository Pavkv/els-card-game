screen witch():

    # Main game screen for witch
    tag witch_screen
    zorder 1

    if card_game.state not in ["wait_choice", "player_turn"]:
         timer 0.5 action Jump(card_game_name + "_game_loop")
    else:
        frame:
            background None
            xpos 1750
            ypos 945
            if len(card_game.player.hand) < 6 and len(card_game.deck.cards) > 0 and not made_turn:
                frame:
                    xsize 150
                    padding (0, 0)
                    has vbox
                    textbutton "{color=#fff}Взять{/color}":
                        style "card_game_button"
                        text_size 25
                        action [Function(draw_anim, 0), SetVariable("made_turn", True)]

            elif card_game.player.count_pairs_excluding_witch() > 0:
                if made_turn:
                    $ action = [
                        Function(discard_pairs_anim, 0),
                        SetVariable("made_turn", False),
                        SetVariable("card_game.state", "opponent_turn"),
                        Jump(card_game_name + "_game_loop")
                    ]
                else:
                    $ action = [
                        Function(discard_pairs_anim, 0)
                    ]

                frame:
                    xsize 150
                    padding (0, 0)
                    has vbox
                    textbutton "{color=#fff}Скинуть\nпары{/color}":
                        style "card_game_button"
                        text_size 18
                        action action

            elif card_game.player.can_exchange_now(card_game.deck) and card_game.state != "wait_choice" and len(card_game.opponent.hand) == 0:
                timer 0.5 action SetVariable("card_game.state", "opponent_turn")

            elif card_game.player.can_exchange_now(card_game.deck) and card_game.state != "wait_choice" and len(card_game.opponent.hand) > 0:
                frame:
                    xsize 150
                    padding (0, 0)
                    has vbox
                    textbutton "{color=#fff}Вытянуть\nкарту{/color}":
                        style "card_game_button"
                        text_size 18
                        action SetVariable("card_game.state", "wait_choice")