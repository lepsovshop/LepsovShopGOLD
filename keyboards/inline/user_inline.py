# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Кнопки при поиске профиля через админ-меню
open_profile_inl = InlineKeyboardMarkup()
input_kb = InlineKeyboardButton(text="✏️Ввести промокод", callback_data="promo_get")#
inputm_kb = InlineKeyboardButton(text="🫂Реферальная система", callback_data="ref_sistem")
#mybuy_kb = InlineKeyboardButton(text="🛒 Мои покупки", callback_data="my_buy")
open_profile_inl.add(input_kb, inputm_kb)

ref_kb = InlineKeyboardMarkup()
ref_kb.add(InlineKeyboardButton(text="Мои рефералы", callback_data="my_ref"))
ref_kb.add(InlineKeyboardButton(text="Назад", callback_data="user_profil"))



# Кнопка с возвратом к профилю
to_ref_kb = InlineKeyboardMarkup()
to_ref_kb.add(InlineKeyboardButton(text="Назад", callback_data="ref_sistem"))
