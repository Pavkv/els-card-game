label start_els:
    $ start_card_game(ElsGame, "els")

label els_game_loop:
    if is_dealing:
#         $ renpy.block_rollback()
        $ is_dealing = False
        call screen deal_cards
    else:
        $ deal_cards = False

    if card_game.round == 5:
#         $ renpy.block_rollback()
        $ game_result_els()

    if card_game.state == "result":
#       $ renpy.block_rollback()
        pause 3.0
        hide screen card_game_base_ui
        if in_game:
            jump expression card_game_results[card_game.result]
        else:
            if card_game.result == card_game.player.name:
                "Вы выиграли!"
            elif card_game.result == card_game.opponent.name:
                "Вы проиграли."
            else:
                "Ничья."
            jump card_games

    if card_game.state == "opponent_turn":
#         $ renpy.block_rollback()
        $ els_opponent_turn()

    call screen els
    jump els_game_loop


