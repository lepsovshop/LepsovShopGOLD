# - *- coding: utf- 8 - *-
from aiogram.dispatcher.filters.state import State, StatesGroup


class StorageUsers(StatesGroup):
    here_input_count_buy_item = State()
    here_cache_position_id = State()
    here_cache_count_item = State()
    here_cache_url = State()

    get_gold = State()

    get_gold_com = State()
    get_gold_nick = State()
    get_gold_minus = State()
    get_rek_minus = State()

    get_promo = State()
