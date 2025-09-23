label start:
    $ player_name = renpy.input("Введите ваше имя", length=20)
    $ opponent_name = "Противник"
    $ cards_bg = "images/bg/bg_14.jpg"
    $ in_game = False
    $ base_card_img_src = "images/cards/cards"
    $ biased_draw = ["opponent", 0.5]
    $ day2_game_with_Alice = False
    python:
        card_game = ElsGame(player_name, opponent_name, biased_draw)
        card_game_name = "els"
        base_cover_img_src = base_card_img_src + "/cover.png"
        card_game.opponent.avatar = card_game_avatar
        card_game.start_game()
        compute_hand_layout()

        dealt_cards = []
        is_dealing = True
        deal_cards = True

        delay = 0.0
        for i in range(len(card_game.player.hand)):
            dealt_cards.append({
                "owner": "player",
                "index": i,
                "delay": delay
            })
            delay += 0.1

        for i in range(len(card_game.opponent.hand)):
            dealt_cards.append({
                "owner": "opponent",
                "index": i,
                "delay": delay
            })
            delay += 0.1

    show screen card_game_base_ui
    jump els_game_loop

label els_game_loop:
    if is_dealing:
#         $ renpy.block_rollback()
        $ is_dealing = False
        call screen deal_cards
    else:
        $ deal_cards = False

    if card_game.state == "results":
#       $ renpy.block_rollback()
        "[card_game.result]"
#         pause 3.0
#         hide screen card_game_base_ui
#         if in_game:
#             if card_game.result == player_name and card_game.player.total21() == 21 and ['7', 'Q', 'A'] in card_game.player.get_ranks():
#                 if not persistent.achievements["Три карты"]:
#                     play sound sfx_achievement
#                     show three_cards_message at achievement_trans
#                     with dspr
#                     $ renpy.pause(3, hard=True)
#                     hide three_cards_message
#                     $ persistent.achievements["Три карты"] = True
#             if card_game.result == player_name and card_game.player.total21() == 21 and ['7', '7', '7'] == card_game.player.get_ranks():
#                 if not persistent.achievements["Три топора"]:
#                     play sound sfx_achievement
#                     show three_axes_message at achievement_trans
#                     with dspr
#                     $ renpy.pause(3, hard=True)
#                     hide three_axes_message
#                     $ persistent.achievements["Три топора"] = True
#             jump expression card_game_results[card_game.result]
#         else:
#             jump card_games

    if card_game.state == "opponent_turn":
#         $ renpy.block_rollback()
        pause 1.5
        python:
            global selected_exchange_card_index_player

            selected_exchange_card_index_player = card_game.opponent_attack()

            if card_game.turn < 2:
                card_game.state = "player_defend"
            else:
                els_ai_take_from_user_anim(selected_exchange_card_index_player)

            compute_hand_layout()

    if card_game.round >= 4:
#         $ renpy.block_rollback()
        $ card_game.result = card_game.game_over()
        $ print("Game Over: ", card_game.result)
        $ card_game.state = "results"

    call screen els
    jump els_game_loop


