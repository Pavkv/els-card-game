label start:
    $ player_name = renpy.input("Введите ваше имя", length=20)
    $ opponent_name = "Противник"
    $ cards_bg = "images/bg/bg_14.jpg"
    $ in_game = False
    $ base_card_img_src = "images/cards/cards"
    $ biased_draw = ["opponent", 0.5]
    $ day2_game_with_Alice = False
    $ g21_card_num = 1
    $ g21_aces_low = False
    $ start_card_game(Game21, "g21", game_kwargs={"initial_deal": g21_card_num, "aces_low": g21_aces_low})

label g21_game_loop:
    if is_dealing:
#         $ renpy.block_rollback()
        $ is_dealing = False
        call screen deal_cards
    else:
        $ deal_cards = False

    if card_game.state == "result":
#       $ renpy.block_rollback()
        pause 3.0
        hide screen card_game_base_ui
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


    if card_game.result:
#         $ renpy.block_rollback()
        $ print("Game Over: ", card_game.result)
        $ card_game.state = "result"

    if card_game.state == "opponent_turn":
#         $ renpy.block_rollback()
        $ g21_opponent_turn()

    call screen game21
    jump g21_game_loop


