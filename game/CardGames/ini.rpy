init:
    # init
    default card_game = None
    default card_game_name = None
    default player_name = None
    default opponent_name = None
    default base_card_img_src = None
    default base_cover_img_src = None
    default cards_bg = None
    default in_game = True
    default card_game_results = {}
    default card_game_avatar = None
    default biased_draw = None
    default made_turn = False

    # Layout constants
    default DECK_X = 13
    default DECK_Y = 373
    default DISCARD_X = 1600
    default DISCARD_Y = 350
    default HAND0_X = 700
    default HAND0_Y = 825
    default HAND1_X = 700
    default HAND1_Y = 20
    default HAND_SPACING = 118

    # Card selection and layout state
    default hovered_card_index = -1
    default hovered_card_index_exchange = -1
    default selected_card_indexes = set()
    default selected_attack_card_indexes = set()
    default selected_exchange_card_index_player = -1
    default selected_exchange_card_index_opponent = -1

    # Turn and animation state
    default deal_cards = True
    default next_turn = True
    default dealt_cards = []
    default is_dealing = False
    default draw_animations = []
    default is_drawing = False
    default table_animations = []
    default is_table_animating = False
    default in_flight_cards = set()

    # Card layouts
    default player_card_layout = []
    default opponent_card_layout = []

    # Suit translations
    default card_suits = {
        "C": "К",
        "D": "Б",
        "H": "Ч",
        "S": "П"
    }

    # Game phase translations
    default card_game_state_tl = {
        "els": {
            "player_turn": "Вы вытягиваете",
            "player_defend": "Вы защищаетесь",
            "opponent_turn": "Противник вытягивает",
            "opponent_defend": "Противник защищается",
            "wait_choice": "Вытягивание карты",
            "wait_choice_opponent": "Противник вытягивает карту",
            "results": "Игра окончена"
        },
        "durak" : {
            "player_turn": "Вы атакуете",
            "player_defend": "Вы защищаетесь",
            "opponent_turn": "Противник атакует",
            "opponent_defend": "Противник защищается",
            "end_turn": "Окончание хода",
            "results": "Игра окончена"
        },
        "g21": {
            "initial_deal": "Раздача",
            "player_turn": "Ваш ход",
            "opponent_turn": "Ход противника",
            "reveal": "Раскрытие",
            "results": "Игра окончена"
        },
        "witch": {
            "player_turn": "Ваш ход",
            "opponent_turn": "Ход противника",
            "opponent_busy": "Ход противника",
            "wait_choice": "Вытягивание карты",
            "wait_choice_opponent": "Противник вытягивает карту",
            "results": "Игра окончена"
        }
    }

    # Card transforms
    transform hover_offset(y=0, x=0):
        easein 0.1 yoffset y xoffset x

    transform no_shift:
        xoffset 0
        yoffset 0

    transform deal_card(dest_x, dest_y, delay=0):
        alpha 0.0
        xpos DECK_X
        ypos DECK_Y
        pause delay
        linear 0.3 alpha 1.0 xpos dest_x ypos dest_y

    transform animate_table_card(x1, y1, x2, y2, delay=0.0, duration=0.4, discard=False):
        alpha 1.0
        xpos x1
        ypos y1
        pause delay

        linear duration xpos x2 ypos y2 alpha 0

    # Styles
    style card_game_button:
        background RoundRect("#b2b3b4", 10)
        hover_background RoundRect("#757e87", 10)
        xsize 150
        padding (5, 5)
        text_align 0.5
        align (0.5, 0.5)

# Show Achievements
label show_achievement(key, message_tag):
    play sound sfx_achievement
    show expression message_tag at achievement_trans
    with dspr
    $ renpy.pause(3, hard=True)
    hide expression message_tag
    $ persistent.achievements[key] = True
    return