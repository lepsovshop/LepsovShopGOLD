# - *- coding: utf- 8 - *-

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from filters import IsWork, IsUser
from filters.all_filters import IsBuy
from keyboards.default import check_user_out_func
from loader import dp, bot
from states import StorageUsers
from utils.db_api.sqlite import *
from utils.other_func import clear_firstname, get_dates

prohibit_buy = ["xbuy_item", "not_buy_items", "buy_this_item", "buy_open_position", "back_buy_item_position",
                "buy_position_prevp", "buy_position_nextp", "buy_category_prevp", "buy_category_nextp",
                "back_buy_item_to_category", "buy_open_category"]


def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1].split("-")[1] if len(text.split()) > 1 else None

# Проверка на нахождение бота на технических работах
@dp.message_handler(IsWork(), state="*")
@dp.callback_query_handler(IsWork(), state="*")
async def send_work_message(message: types.Message, state: FSMContext):
    if "id" in message:
        await message.answer("🔴 Бот находится на технических работах.", parse_mode='HTML')
    else:
        await message.answer("<b>🔴 Бот находится на технических работах.</b>", parse_mode='HTML')


# Обработка кнопки "На главную" и команды "/start"
@dp.message_handler(text="⬅ На главную", state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    first_name = clear_firstname(message.from_user.first_name)
    get_user_id = get_userx(user_id=message.from_user.id)
    if get_user_id is None:
        unique_code = extract_unique_code(message.text)
        if unique_code:
            ref_code = int(unique_code)
        else:
            ref_code = 0
        if message.from_user.username is not None:
            get_user_login = get_userx(user_login=message.from_user.username)
            if get_user_login is None:
                add_userx(message.from_user.id, message.from_user.username.lower(), first_name, 0, 0, get_dates(), ref_code)
            else:
                delete_userx(user_login=message.from_user.username)
                add_userx(message.from_user.id, message.from_user.username.lower(), first_name, 0, 0, get_dates(), ref_code)
        else:
            add_userx(message.from_user.id, message.from_user.username, first_name, 0, 0, get_dates(), ref_code)
    else:
        if first_name != get_user_id[3]:
            update_userx(get_user_id[1], user_name=first_name)
        if message.from_user.username is not None:
            if message.from_user.username.lower() != get_user_id[2]:
                update_userx(get_user_id[1], user_login=message.from_user.username.lower())
    curs = get_settingsp("curs")
    await message.answer(f"""▶️ Для продолжения выбери нужную команду на клавиатуре 👇
🙋‍♂️ Если есть дополнительные вопросы по поводу бота, обратитесь в Тех.Поддержку
📊 Курс: {curs*100}₽ за 100 голды коммисия на нас💰""",
                         reply_markup=check_user_out_func(message.from_user.id), parse_mode='HTML')



@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    first_name = clear_firstname(message.from_user.first_name)
    get_user_id = get_userx(user_id=message.from_user.id)
    if get_user_id is None:
        unique_code = extract_unique_code(message.text)
        if unique_code:
            ref_code = int(unique_code)
        else:
            ref_code = 0
        if message.from_user.username is not None:
            get_user_login = get_userx(user_login=message.from_user.username)
            if get_user_login is None:
                add_userx(message.from_user.id, message.from_user.username.lower(), first_name, 0, 0, get_dates(), ref_code)
            else:
                delete_userx(user_login=message.from_user.username)
                add_userx(message.from_user.id, message.from_user.username.lower(), first_name, 0, 0, get_dates(), ref_code)
        else:
            add_userx(message.from_user.id, message.from_user.username, first_name, 0, 0, get_dates(), ref_code)
    else:
        if first_name != get_user_id[3]:
            update_userx(get_user_id[1], user_name=first_name)
        if message.from_user.username is not None:
            if message.from_user.username.lower() != get_user_id[2]:
                update_userx(get_user_id[1], user_login=message.from_user.username.lower())
    curs = get_settingsp("curs")
    await message.answer(f"""▶️ Для продолжения выбери нужную команду на клавиатуре 👇

💰 Нажмите "Пополнить баланс" после купите золото и ждите вывода! 🥝
За приглашенного друга мы платим 5 голды, удачи! 🐋

🙋‍♂️ Если есть дополнительные вопросы по поводу бота, обратитесь в Тех.Поддержку
@lepsov_original - Создатель бота⬇️
📊 Курс: {round(curs*100)}₽ за 100 голды💵""",
                         reply_markup=check_user_out_func(message.from_user.id), parse_mode='HTML')


@dp.message_handler(IsUser(), state="*")
@dp.callback_query_handler(IsUser(), state="*")
async def send_user_message(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_user.id,
                           "<b>❗ Ваш профиль не был найден.</b>\n"
                           "▶ Введите /start", parse_mode='HTML')


# Проверка на доступность покупок
@dp.message_handler(IsBuy(), text="🎁 Купить", state="*")
@dp.message_handler(IsBuy(), state=StorageUsers.here_input_count_buy_item)
@dp.callback_query_handler(IsBuy(), text_startswith=prohibit_buy, state="*")
async def send_user_message(message, state: FSMContext):
    if "id" in message:
        await message.answer("🔴 Покупки в боте временно отключены", True, parse_mode='HTML')
    else:
        await message.answer("<b>🔴 Покупки в боте временно отключены</b>", parse_mode='HTML')
