# - *- coding: utf- 8 - *-
from aiogram.dispatcher.filters.state import State, StatesGroup


class StorageQiwi(StatesGroup):
    here_input_qiwi_secret = State()
    here_input_qiwi_login = State()
    here_input_qiwi_token = State()
    here_input_qiwi_amount = State()

    here_input_sber_amount = State()
    here_input_img_amount = State()
    here_input_sber_rek = State()
    here_input_sber_min = State()
