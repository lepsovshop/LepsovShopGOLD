# - *- coding: utf- 8 - *-
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from keyboards.default import check_user_out_func, all_back_to_main_default
from keyboards.default.menu import *
from keyboards.inline import *
from keyboards.inline.inline_page import *
from loader import dp, bot
from utils import send_all_admin, clear_firstname, get_dates
from states.state_users import *
from states.state_payment import *
from utils.other_func import clear_firstname, get_dates
import traceback
#from utils.db_api.sqlite import 


# Разбив сообщения на несколько, чтобы не прилетало ограничение от ТГ
def split_messages(get_list, count):
    return [get_list[i:i + count] for i in range(0, len(get_list), count)]




# Обработка кнопки "Купить"
@dp.message_handler(text="🎳 Игры", state="*")
async def show_search(message: types.Message, state: FSMContext):
    await state.finish()
    get_categories = get_all_categoriesx(upcategories=1)
    if len(get_categories) >= 1:
        get_kb = buy_item_open_category_ap(0, 1)
        await message.answer("<b>📦 Выберите категорию:</b>", reply_markup=get_kb, parse_mode='HTML')
    else:
        await message.answer("<b>📦 Товары в данное время отсутствуют.</b>", parse_mode='HTML')


@dp.message_handler(text="🍯 Купить голду", state="*")
async def show_search(message: types.Message, state: FSMContext):
    await state.finish()
    get_user = get_userx(user_id=message.from_user.id)
    get_curs = get_settingsp("curs")
    p_kb = InlineKeyboardMarkup()
    p_kb.add(InlineKeyboardButton(text="Пополнить", callback_data="plus_kb"))
    if get_user[4] > 10:
        await StorageUsers.get_gold.set()
        await message.answer(f"""<b>🎖️ Введите количество золота для пополнения</b>

Вы можете купить {round(int(get_user[4])/get_curs, 2)} голды""", reply_markup=all_back_to_main_default, parse_mode='HTML')
    else:
        await message.answer("<b>❗️ На вашем балансе нету денег</b>",reply_markup=p_kb, parse_mode='HTML')


@dp.message_handler(state=StorageUsers.get_gold)
async def input_new_position_price(message: types.Message, state: FSMContext):
    try:
        msg = round(float(message.text.replace(",", ".").replace(" ", "")), 2)
        get_user = get_userx(user_id=message.from_user.id)
        get_curs = get_settingsp("curs")
        p_kb = InlineKeyboardMarkup()
        p_kb.add(InlineKeyboardButton(text="Пополнить", callback_data="plus_kb"))
        if msg*get_curs >= get_user[4]:
            await message.answer("<b>❗️ У вас нехватает баланса</b>", reply_markup=p_kb, parse_mode='HTML')
        else:
            update_userx(message.from_user.id, balance=round(get_user[4] - msg*get_curs, 2))
            update_userx(message.from_user.id, all_refill=get_user[5] + msg)
            key_menu = check_user_out_func(message.from_user.id)
            update_userx(message.from_user.id, all_pay=round(int(get_user[8]) + msg))
            await message.answer(f"""🍯 Ваш баланс золота был пополнен на {msg}G""", reply_markup = key_menu, parse_mode='HTML')
            if msg>=30 and get_user[7] != 0:
                get_user_id = get_userx(increment=get_user[7])[1]
                get_user_gold = get_userx(increment=get_user[7])[5]
                update_userx(get_user_id, all_refill=get_user_gold + 5)
                await bot.send_message(get_user_id, "Вы получили 5 голды за реферала")
            await state.finish()
    except:
        await message.answer("Неверно введена сумма голды", parse_mode='HTML')


# Обработка кнопки "Профиль"
@dp.message_handler(text="Профиль 📝", state="*")
async def show_profile(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(get_user_profile(message.from_user.id), 
        reply_markup=open_profile_inl, parse_mode='HTML')
    


# Обработка кнопки "FAQ"
@dp.message_handler(text="Отзывы 👤", state="*")
async def show_my_deals(message: types.Message, state: FSMContext):
    await state.finish()
    get_settings = get_settingsx()
    send_msg = get_settings[1]
    if "{username}" in send_msg:
        send_msg = send_msg.replace("{username}", f"<b>{message.from_user.username}</b>")
    if "{user_id}" in send_msg:
        send_msg = send_msg.replace("{user_id}", f"<b>{message.from_user.id}</b>")
    if "{firstname}" in send_msg:
        send_msg = send_msg.replace("{firstname}", f"<b>{clear_firstname(message.from_user.first_name)}</b>")
    await message.answer(send_msg, disable_web_page_preview=True, parse_mode='HTML')


# Обработка кнопки "Поддержка"
@dp.message_handler(text="Тех. Поддержка 👥", state="*")
async def show_contact(message: types.Message, state: FSMContext):
    await state.finish()
    get_settings = get_settingsx()
    pd_kb = InlineKeyboardMarkup(row_width=3)
    pd_kb.add(InlineKeyboardButton(text="1", callback_data="pd_kb:1"),
    InlineKeyboardButton(text="2", callback_data="pd_kb:2"),
    InlineKeyboardButton(text="3", callback_data="pd_kb:3"))
    pd_kb.add(InlineKeyboardButton(text="4", callback_data="pd_kb:4"),
        InlineKeyboardButton(text="5", callback_data="pd_kb:5"),
        InlineKeyboardButton(text="6", callback_data="pd_kb:6"))
    pd_kb.add(InlineKeyboardButton(text="Связаться", url=get_settings[0]))
    await message.answer("""1. Сколько по времени выводят золото?
2. Почему так долго проверяют чек?
3. Почему так долго выводят золото?
4. Почему мне не пришли деньги?
5. Безопасно ли у вас покупать?
6. Можно ли вам продать золото/кланы/аккаунт/скины?
""", reply_markup=pd_kb, disable_web_page_preview=True, parse_mode='HTML')

@dp.callback_query_handler(text_startswith="return_pd", state="*")
async def show_referral(call: CallbackQuery, state: FSMContext):
    await state.finish()
    get_settings = get_settingsx()
    pd_kb = InlineKeyboardMarkup(row_width=3)
    pd_kb.add(InlineKeyboardButton(text="1", callback_data="pd_kb:1"),
    InlineKeyboardButton(text="2", callback_data="pd_kb:2"),
    InlineKeyboardButton(text="3", callback_data="pd_kb:3"))
    pd_kb.add(InlineKeyboardButton(text="4", callback_data="pd_kb:4"),
        InlineKeyboardButton(text="5", callback_data="pd_kb:5"),
        InlineKeyboardButton(text="6", callback_data="pd_kb:6"))
    pd_kb.add(InlineKeyboardButton(text="Связаться", url=get_settings[0]))
    await call.message.edit_text("""1. Сколько по времени выводят золото?
2. Почему так долго проверяют чек?
3. Почему так долго выводят золото?
4. Почему мне не пришли деньги?
5. Безопасно ли у вас покупать?
6. Можно ли вам продать золото/кланы/аккаунт/скины?
""", reply_markup=pd_kb, disable_web_page_preview=True, parse_mode='HTML')


# Обработка колбэка "Мои покупки"
@dp.callback_query_handler(text="my_buy", state="*")
async def show_referral(call: CallbackQuery, state: FSMContext):
    last_purchases = last_purchasesx(call.from_user.id)
    if len(last_purchases) >= 1:
        await call.message.delete()
        count_split = 0
        save_purchases = []
        for purchases in last_purchases:
            save_purchases.append(f"<b>📃 Чек:</b> <code>#{purchases[4]}</code>\n"
                                  f"▶ {purchases[9]} | {purchases[5]}шт | {purchases[6]} руб\n"
                                  f"🕜 {purchases[13]}\n"
                                  f"<code>{purchases[10]}</code>")
        await call.message.answer("<b>🛒 Последние 10 покупок</b>\n"
                                  "➖➖➖➖➖➖➖➖➖➖➖➖➖", parse_mode='HTML')
        save_purchases.reverse()
        len_purchases = len(save_purchases)
        if len_purchases > 4:
            count_split = round(len_purchases / 4)
            count_split = len_purchases // count_split
        if count_split > 1:
            get_message = split_messages(save_purchases, count_split)
            for msg in get_message:
                send_message = "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n".join(msg)
                await call.message.answer(send_message, parse_mode='HTML')
        else:
            send_message = "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n".join(save_purchases)
            await call.message.answer(send_message, parse_mode='HTML')

        await call.message.answer(get_user_profile(call.from_user.id), reply_markup=open_profile_inl, parse_mode='HTML')
    else:
        await call.answer("❗ У вас отсутствуют покупки")

        
# Баланс

@dp.callback_query_handler(text_startswith="plus_kb", state="*")
async def open_user_profil(call: CallbackQuery, state: FSMContext):
    await state.finish()
    get_user = get_userx(user_id=call.from_user.id)
    min_amm = get_settingsp("sber_min")
    await call.message.delete()
    await bot.send_message(call.from_user.id, f"""💵 Введите сумму, которую вы хотите пополнить на баланс. Например: 60

💰 Минимальная сумма пополнения: {min_amm}р

❗️ Обязательно введите целое число""", reply_markup=all_back_to_main_default, parse_mode='HTML')
    await StorageQiwi.here_input_sber_amount.set()


@dp.message_handler(text="Пополнить баланс 💳", state="*")
async def show_contact(message: types.Message, state: FSMContext):
    await state.finish()
    await StorageQiwi.here_input_sber_amount.set()
    get_user = get_userx(user_id=message.from_user.id)
    min_amm = get_settingsp("sber_min")
    await bot.send_message(message.from_user.id, f"""💰Введите сумму, которую вы хотите пополнить на баланс. Например: 60

💵Минимальная сумма пополнения: {min_amm}р

❗️ Обязательно введите целое число""", reply_markup=all_back_to_main_default, parse_mode='HTML')
    
@dp.message_handler(text="Вывести голду🍯", state="*")
async def show_contact(message: types.Message, state: FSMContext):
    await state.finish()
    get_user = get_userx(user_id=message.from_user.id)
    if get_user[5] < 100:
        await bot.send_message(message.from_user.id, f"""❗️ Вывод работает от 100 голды""")
    else:
        await StorageUsers.get_gold_minus.set()
        await bot.send_message(message.from_user.id, f"""🍯 Введите количество голды для вывода (у вас {get_user[5]}):""", reply_markup=all_back_to_main_default, parse_mode='HTML')

@dp.message_handler(state=StorageUsers.get_gold_minus)
async def input_new_posion_price(message: types.Message, state: FSMContext):
    try:
        msg = int(message.text.replace(",", ".").replace(" ", ""))
        get_user = get_userx(user_id=message.from_user.id)
        if msg < 100:
            await message.answer(f"""❗️ Вывод работает от 100 голды""")
        else:
            if get_user[5] >= msg:
                tovar = get_settingsp("tovar")
                summ_com = msg + ((msg/100)*get_settingsp("com")) + (random.choice(list(range(1,100)))/100)
                summ = msg
                async with state.proxy() as data:
                    data["get_gold_nick"] = f"{get_user[1]}"
                    data["get_gold_minus"] = summ
                    data["get_gold_com"] = summ_com
                await StorageUsers.get_rek_minus.set()
                await message.answer(f"""Отлично 🙌
🌴 Для начала сделайте ваш Nickname в стандофф :
WWWWWWWWWWWWWWWWWW
Чтобы избежать фейков.



Теперь выставите {tovar} скин за {summ_com} голды, чтобы вам пришло {summ} голды
И нажмите на кнопку "Только мои запросы", сделайте скриншот и отправьте его сюда.

❗️ Всю комиссию рынка мы берём на себя. Выставляйте именно за {summ_com}, чтобы вам пришло {summ} голды, и чтобы ваш скин было легко найти.

🥽ОБЯЗАТЕЛЬНО СКИНЬТЕ СКРИНШТОТ СКИНА ПОСЛЕ ЭТОГО СООБЩЕНИЯ💍""", parse_mode='HTML')
            else:
                await message.answer("У вас нехватает голды🍯", parse_mode='HTML')

    except:
        await message.answer("Неверно введена сумма голды🍯", parse_mode='HTML')
        


@dp.message_handler(content_types=["photo"], state=StorageUsers.get_rek_minus)
async def position_get_image(message: types.Message, state: FSMContext):
    photo = message.text
    get_user = get_userx(user_id=message.from_user.id)
    async with state.proxy() as data:
        gold = data["get_gold_minus"]
        summ_com = data["get_gold_com"]
        nick = data["get_gold_nick"]
    if get_user[5] >= gold:
        await state.finish()
        key_menu = check_user_out_func(message.from_user.id)

        bal_minus = InlineKeyboardMarkup()
        bal_minus.add(InlineKeyboardButton(text="✅Подтвердить", callback_data=f"minus_pr:{message.from_user.id}:{gold}"))
        bal_minus.add(InlineKeyboardButton(text="❌Отменить", callback_data=f"minus_ot:{message.from_user.id}:{gold}"))
        ball_g = get_user[5]
        update_userx(message.from_user.id, all_refill = round(ball_g - gold, 2))
        await message.answer(f"""💰 Заявка на Вывод {gold}G выставлена 
Ожидайте своей очереди! 💰
💵Также загляните в акции!""", reply_markup = key_menu, parse_mode='HTML')
        await send_all_admin(f"""<b>Заявка на вывод</b>
👤 Пользователь: <a href='tg://user?id={get_user[1]}'>{get_user[3]}</a> (<code>{get_user[1]}</code>)
        
Никнейм: <code>{nick}</code>
Сумма голды: <code>{gold}</code>
Сумма голды с комиссией: <code>{summ_com}</code>""", markup=bal_minus, photo = message.photo[0].file_id)
    else:
        await message.answer("У вас нехватает голды🍯", parse_mode='HTML')

    
@dp.callback_query_handler(text_startswith="user_profil", state="*")
async def open_user_profil(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(get_user_profile(call.from_user.id), reply_markup=open_profile_inl, parse_mode='HTML')

@dp.callback_query_handler(text_startswith="sber_plus", state="*")
async def open_user_profil(call: CallbackQuery, state: FSMContext):
    amm = int(call.data.split(":")[1])
    await state.finish()
    sber_rek = get_settingsp("sber_rek")
    async with state.proxy() as data:
        data["here_input_sber_amount"] = amm
    await call.message.edit_text(f"""📩 Отправьте деньги на Сбербанк по реквизитам:
💳 По номеру карты: <code>{sber_rek}</code>
💬 Комментарий: <code>tb: {call.from_user.id}</code>
💲 Сумма: <code>{amm}</code>₽

📷 Отправьте нам скриншот чека""", parse_mode='HTML')
    await StorageQiwi.here_input_img_amount.set()

@dp.message_handler(state=StorageQiwi.here_input_sber_amount)
async def here_input_sber_amount(message: types.Message, state: FSMContext):
    try:
        amm = int(message.text)
        min_amm = get_settingsp("sber_min")
        if amm >= min_amm:
            minus_ball_kb = InlineKeyboardMarkup(row_width=1)
            minus_ball_kb.add(InlineKeyboardButton(text="🥝Киви", callback_data=f"user_input:{message.text}"))
            minus_ball_kb.add(InlineKeyboardButton(text="🟢Сбербанк", callback_data=f"sber_plus:{message.text}"))
            curs = get_settingsp("curs")
            await message.answer(f"""⭐️ За {message.text} рублей вы сможете купить {round(int(message.text)/curs, 2)} золота
🖋 Выберите наиболее удобный для вас способ оплаты
""", reply_markup=minus_ball_kb, parse_mode='HTML')
            await state.finish()
        else:
            await message.answer(f"""Мин сумма пополнения {min_amm} руб.""")
    except:
        await message.answer(f"""Неверно введена сумма пополнения""")


@dp.message_handler(content_types=["photo"], state=StorageQiwi.here_input_img_amount)
async def position_get_image(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        ammount = data["here_input_sber_amount"]
    kb_kb = check_user_out_func(message.from_user.id)
    await message.answer(f"""Ваша заявка принята""", reply_markup=kb_kb, parse_mode='HTML')
    minus_ball_kb = InlineKeyboardMarkup(row_width=2)
    minus_ball_kb.add(InlineKeyboardButton(text="Принять", callback_data=f"sber_pr:{message.from_user.id}:{ammount}"))
    minus_ball_kb.add(InlineKeyboardButton(text="Отклонить", callback_data=f"sber_ot:{message.from_user.id}:{ammount}"))
    get_user = get_userx(user_id=message.from_user.id)
    position_photo = message.photo[0].file_id
    await send_all_admin(f"""Пополнение баланса
Пользователь: <a href='tg://user?id={get_user[1]}'>{get_user[3]}</a> <code>({get_user[1]})</code>
Сумма: {ammount} руб.
Коментарий: <code>tb: {message.from_user.id}</code>""", markup=minus_ball_kb, photo = position_photo)

    await state.finish()
    
################################################################################################
######################################### ПОКУПКА ТОВАРА #######################################
# Открытие категории для покупки
@dp.callback_query_handler(text_startswith="buy_open_category", state="*")
async def open_category_for_buy_item(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    get_category = get_categoryx("*", category_id=category_id)
    get_positions = get_positionsx("*", category_id=category_id)
    get_all_podcategories1 = get_all_categoriesx(upcategories=category_id)
    if len(get_all_podcategories1) > 0:
        get_categories = get_all_categoriesx(upcategories=category_id)
        if len(get_categories) >= 1:
            get_kb = buy_item_open_category_ap(0, category_id)
            await call.message.edit_text("<b>📦 Выберите категорию:</b>", reply_markup=get_kb, parse_mode='HTML')
        else:
            await call.message.edit_text("<b>📦 Товары в данное время отсутствуют.</b>", parse_mode='HTML')
    else:
        get_kb = buy_item_item_position_ap(0, category_id)
        if len(get_all_podcategories1) > 0:
            get_kb = buy_item_open_category_ap(0, category_id)
            await call.message.edit_text("<b>📦 Выберите категорию:</b>", reply_markup=get_kb, parse_mode='HTML')
        else:
            if len(get_positions) >= 1:
                await call.message.edit_text("<b>📦 Выберите нужный вам товар:</b>",
                                             reply_markup=get_kb, parse_mode='HTML')
            else:
                await call.answer(f"❕ Товары в категории {get_category[2]} отсутствуют.")


# Вернутсья к предыдущей категории при покупке
@dp.callback_query_handler(text_startswith="back_buy_item_to_category", state="*")
async def back_category_for_buy_item(call: CallbackQuery, state: FSMContext):
    up_cat = int(call.data.split(":")[1])
    await call.message.edit_text("<b>📦 Выберите нужный вам товар:</b>",
                                 reply_markup=buy_item_open_category_ap(0, up_cat), parse_mode='HTML')


# Следующая страница категорий при покупке
@dp.callback_query_handler(text_startswith="buy_category_nextp", state="*")
async def buy_item_next_page_category(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text("<b>📦 Выберите нужный вам товар:</b>",
                                 reply_markup=buy_item_next_page_category_ap(remover), parse_mode='HTML')


# Предыдущая страница категорий при покупке
@dp.callback_query_handler(text_startswith="buy_category_prevp", state="*")
async def buy_item_prev_page_category(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text("<b>📦 Выберите нужный вам товар:</b>",
                                 reply_markup=buy_item_previous_page_category_ap(remover), parse_mode='HTML')


# Следующая страница позиций при покупке
@dp.callback_query_handler(text_startswith="buy_position_nextp", state="*")
async def buy_item_next_page_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])

    await call.message.edit_text("<b>📦 Выберите нужный вам товар:</b>",
                                 reply_markup=item_buy_next_page_position_ap(remover, category_id), parse_mode='HTML')


# Предыдущая страница позиций при покупке
@dp.callback_query_handler(text_startswith="buy_position_prevp", state="*")
async def buy_item_prev_page_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])

    await call.message.edit_text("<b>📦 Выберите нужный вам товар:</b>",
                                 reply_markup=item_buy_previous_page_position_ap(remover, category_id), parse_mode='HTML')


# Возвращение к страницам позиций при покупке товара
@dp.callback_query_handler(text_startswith="back_buy_item_position", state="*")
async def buy_item_next_page_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])
    await call.message.delete()
    await call.message.answer("<b>📦 Выберите нужный вам товар:</b>",
                              reply_markup=buy_item_item_position_ap(remover, category_id), parse_mode='HTML')


# Открытие позиции для покупки
@dp.callback_query_handler(text_startswith="buy_open_position", state="*")
async def open_category_for_create_position(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[2])
    remover = int(call.data.split(":")[3])
    category_id = int(call.data.split(":")[4])
    get_position = get_positionx("*", position_id=position_id)
    get_category = get_categoryx("*", category_id=category_id)
    delete_msg = await call.message.answer("<b>🔄 Ждите, товары подготавливаются</b>", parse_mode='HTML')
    await delete_msg.delete()
    send_msg = f"<b>🏷 Название:</b> <code>{get_position[2]}</code>\n\n" \
               f"<b>💵 Стоимость:</b> <code>{get_position[3]} руб</code>\n\n" \
               f"<b>📜 Описание:</b>\n\n" \
               f"{get_position[4]}\n"
    if len(get_position[5]) >= 5:
        await call.message.delete()
        await call.message.answer_photo(get_position[5],
                                        send_msg,
                                        reply_markup=confirm_buy_items(remover, position_id, delete_msg.from_user.id, category_id, get_position[3]), parse_mode='HTML')
    else:
        await call.message.edit_text(send_msg,
                                     reply_markup=confirm_buy_items(remover, position_id, delete_msg.from_user.id, category_id, get_position[3]), parse_mode='HTML')






# Согласие на покупку товара
@dp.callback_query_handler(text_startswith="xbuy_item:", state="*")
async def yes_buy_this_item(call: CallbackQuery, state: FSMContext):
    get_settings = get_settingsx()
    delete_msg = await call.message.answer("<b>🔄 Ждите, товары подготавливаются</b>", parse_mode='HTML')
    position_id = int(call.data.split(":")[1])
    get_count = int(call.data.split(":")[2])
    message_id = int(call.data.split(":")[3])
    url = call.data.split(":")[4]

    await delete_msg.delete()

    get_position = get_positionx("*", position_id=position_id)
    get_user = get_userx(user_id=call.from_user.id)
    amount_pay = int(get_position[3]) * get_count

    if True:
        if int(get_user[4]) >= amount_pay:
            amount_pay = int(get_position[3]) * get_count

            random_number = [random.randint(100000000, 999999999)]
            passwd = list("ABCDEFGHIGKLMNOPQRSTUVYXWZ")
            random.shuffle(passwd)
            random_char = "".join([random.choice(passwd) for x in range(1)])
            receipt = random_char + str(random_number[0])
            buy_time = get_dates()

            
            add_purchasex(call.from_user.id, call.from_user.username, call.from_user.first_name,
                          receipt, 0, amount_pay, get_position[3], get_position[1], get_position[2],
                          0, get_user[4], int(get_user[4]) - amount_pay, buy_time, int(time.time()), url)
            update_userx(call.from_user.id, balance=get_user[4] - amount_pay)
            win = random.choice(eval(get_position[8]))
            await call.message.answer(f"Ваш выигрышь {win} голды", reply_markup=check_user_out_func(call.from_user.id), parse_mode='HTML')
            update_userx(call.from_user.id, balance=get_user[4] - amount_pay)
            update_userx(call.from_user.id, all_refill=get_user[5] + win)
            await send_all_admin(f"<b>📦 Человек купил товары ✅</b>\n"
                                      f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                      f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                      f"📃 Чек: <code>#{receipt}</code>\n"
                                      f"🏷 Название товара: <code>{get_position[2]}</code>\n"
                                      f"📦 Куплено товаров: <code>{get_count}</code>\n"
                                      f"💵 Сумма покупки: <code>{amount_pay} руб</code>\n"
                                      f"👤 Покупатель: <a href='tg://user?id={get_user[1]}'>{get_user[3]}</a> <code>({get_user[1]})</code>\n"
                                      f"🕜 Дата покупки: <code>{buy_time}</code>")
        else:
            await call.message.answer("<b>❗ На вашем счёте недостаточно средств</b>", parse_mode='HTML')
    else:
        await state.finish()
        await call.message.answer("<b>📦 Товар который вы хотели купить закончился или изменился.</b>",
                                  check_user_out_func(call.from_user.id))

@dp.callback_query_handler(text_startswith="ref_sistem", state="*")
async def buy_item_next_page_position(call: CallbackQuery, state: FSMContext):
    await state.finish()
    id = get_userx(user_id=call.from_user.id)[0]
    await call.message.edit_text(f"""🔗 Ваша реферальная ссылка - <code>t.me/Gg123455_bot?start=ref-{id}</code>

📤 Отправьте её вашим друзьям. Если Ваш друг зарегистрируется по ссылке и задонатит, то вы получите 5 голды на баланс!""",
                                 reply_markup=ref_kb, parse_mode='HTML')


@dp.callback_query_handler(text_startswith="my_ref", state="*")
async def buy_item_next_page_position(call: CallbackQuery, state: FSMContext):
    id = get_userx(user_id=call.from_user.id)[0]
    col = len(get_usersx(ref_code=id))
    await state.finish()
    await call.message.edit_text(f"""👤 У вас {col} рефералов""",
                                 reply_markup=to_ref_kb, parse_mode='HTML')

@dp.callback_query_handler(text_startswith="promo_get", state="*")
async def buy_item_next_page_position(call: CallbackQuery, state: FSMContext):
    id = get_userx(user_id=call.from_user.id)
    await call.message.delete()
    msg_del = await bot.send_message(call.from_user.id, f"""Введите промокод""", reply_markup=all_back_to_main_default, parse_mode='HTML')
    await StorageUsers.get_promo.set()

@dp.message_handler(state=StorageUsers.get_promo)
async def get_promo(message: types.Message, state: FSMContext):
    promo = get_itemsx("*", item_data = message.text.replace(" ", ""))
    if promo is None or len(promo) == 0:
        await message.answer("Такого промокода не существует")
    else:
        promo = promo[0]
        if message.from_user.id in eval(promo[4]):
            await message.answer("Вы уже активировали промокод")
        else:
            if promo[3] <= len(eval(promo[4])):
                await message.answer("Количество активаций закончилось")
            else:
                if promo[5] == "голда":
                    get_user = get_userx(user_id=message.from_user.id)
                    update_userx(message.from_user.id, all_refill=get_user[5]+promo[1])
                    list_promo = eval(promo[4])
                    list_promo.append(message.from_user.id)
                    update_itemx(promo[0], kol_get=str(list_promo))
                    await message.answer(f"Промокод на {promo[1]}G активирован", reply_markup=check_user_out_func(message.from_user.id))
                else:
                    get_user = get_userx(user_id=message.from_user.id)
                    update_userx(message.from_user.id, balance=get_user[4]+promo[1])
                    update_itemx(promo[0], kol_get=str(eval(promo[4]).append(message.from_user.id)))
                    await message.answer(f"Промокод на {promo[1]}руб. активирован", reply_markup=check_user_out_func(message.from_user.id))

@dp.callback_query_handler(text_startswith="pd_kb", state="*")
async def pd_kb(call: CallbackQuery, state: FSMContext):
    await state.finish()
    id_v = int(call.data.split(":")[1])
    get_settings = get_settingsx()
    pd_rt = InlineKeyboardMarkup(row_width=2)
    pd_rt.add(InlineKeyboardButton(text="Связаться", url=get_settings[0]),
        InlineKeyboardButton(text="Назад", callback_data="return_pd"))
    if id_v == 1:
        await call.message.edit_text("""Вывод золота происходит до 24 часов от запроса на вывод. Но в большинстве вывод происходит от нескольких секунд до часа.""", reply_markup=pd_rt, disable_web_page_preview=True, parse_mode='HTML')
    if id_v == 2:
        await call.message.edit_text("""Чеки проверяются в ручную, а не автоматически. Если вы пополнили рано утром или поздно вечером, то наши сотрудники не смогут проверить чек. Проверка чека занимает до 24 часов.""", reply_markup=pd_rt, disable_web_page_preview=True, parse_mode='HTML')
    if id_v == 3:
        await call.message.edit_text("""Вывод золота занимает до 24 часов. Но мы стараемся как можно быстрее вывести вам золото. В большинстве случаев, есть очередь, и пока она дойдёт до вас, может пройти немного времени. Но если вы уже пол часа как на 1 месте, это может быть из-за проблем с рынком ( сложно искать скин) или работник взял перерыв.""", reply_markup=pd_rt, disable_web_page_preview=True, parse_mode='HTML')
    if id_v == 4:
        await call.message.edit_text("""Если вы пополняли через QIWI, то найдите сообщение где вам выдали ссылку на оплату, и под этим сообщением будет кнопка «Проверить оплату» нажмите её. Но если вы пополняли другим способом, то вы, возможно, скинули боту чек файлом. В подобном случае, нажмите: ' Пополнить баланс '; укажите сумму; ' Другим способом '; ' Отправить чек '. После, отправьте скриншот чека.""", reply_markup=pd_rt, disable_web_page_preview=True, parse_mode='HTML')
    if id_v == 5:
        await call.message.edit_text("""Весь товар, который продаётся в боте, получен честным путём. Если вы сомневаетесь в безопасности, то лучше покупать в игре.""", reply_markup=pd_rt, disable_web_page_preview=True, parse_mode='HTML')
    if id_v == 6:
        await call.message.edit_text("""Мы не покупаем товары других пользователей, так как, не знаем, откуда они их достали, а если знаем, это не является гарантией безопасности. Безопасность пользователей на первом месте для нас, и мы продаём только свои товары, в которых уверенны на 100%""", reply_markup=pd_rt, disable_web_page_preview=True, parse_mode='HTML')