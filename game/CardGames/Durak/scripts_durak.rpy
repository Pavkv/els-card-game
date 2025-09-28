label start:
    $ player_name = renpy.input("Введите ваше имя", length=20)
    $ opponent_name = "Противник"
    $ cards_bg = "images/bg/bg_14.jpg"
    $ in_game = False
    $ base_card_img_src = "images/cards/cards"
    $ biased_draw = ["opponent", 0.5]
    $ day2_game_with_Alice = False
    $ start_card_game(DurakGame, "durak")

label durak_game_loop:
    if is_dealing:
#         $ renpy.block_rollback()
        $ is_dealing = False
        call screen deal_cards
    else:
        $ deal_cards = False

    if card_game.result:
#         $ renpy.block_rollback()
        $ print("Game Over: ", card_game.result)
        $ card_game.state = "result"

    if card_game.state == "opponent_turn":
#         $ renpy.block_rollback()
        $ durak_opponent_turn()

    elif card_game.state == "opponent_defend":
#         $ renpy.block_rollback()
        $ durak_opponent_defend()

    elif card_game.state == "end_turn":
#         $ renpy.block_rollback()
        $ durak_end_turn()

    if card_game.state == "result":
#       $ renpy.block_rollback()
        hide screen card_game_base_ui
        if in_game:
            if card_game.result == card_game.opponent.name and lost_to_two_sixes:
                if not persistent.achievements["Адмирал"]:
                    play sound sfx_achievement
                    show admiral_message at achievement_trans
                    with dspr
                    $ renpy.pause(3, hard=True)
                    hide admiral_message
                    $ persistent.achievements["Адмирал"] = True
            jump expression card_game_results[card_game.result]
        else:
            $ reset_card_game()
            jump card_games

    call screen durak
    jump durak_game_loop
