label start_witch:
    $ player_name = renpy.input("Введите ваше имя", length=20)
    $ opponent_name = "Противник"
    $ cards_bg = "images/bg/bg_14.jpg"
    $ in_game = False
    $ base_card_img_src = "images/cards/cards"
    $ biased_draw = ["opponent", 0.5]
    $ day2_game_with_Alice = False
    $ last_winner = "player"
    $ start_card_game(WitchGame, "witch")

label witch_game_loop:
    $ print(card_game.player.hand)
    $ print(card_game.opponent.hand)
    if is_dealing:
#         $ renpy.block_rollback()
        $ is_dealing = False
        call screen deal_cards
    else:
        $ deal_cards = False

    $ print(card_game.user_turn)

    if card_game.state == "result":
#       $ renpy.block_rollback()
        pause 3.0
        hide screen card_game_base_ui
        if in_game:
            if card_game.result != player_name:
                if not persistent.achievements["Да ты ведьма!"]:
                    play sound sfx_achievement
                    show you_are_a_witch_message at achievement_trans
                    with dspr
                    $ renpy.pause(3, hard=True)
                    hide you_are_a_witch_message
                    $ persistent.achievements["Да ты ведьма!"] = True
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
        pause 1.5
        $ witch_opponent_turn()

    call screen witch
    jump witch_game_loop


