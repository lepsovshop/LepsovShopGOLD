import json
import random
import time

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from pyqiwip2p import QiwiP2P

from keyboards.default import all_back_to_main_default, check_user_out_func
from keyboards.inline import *
from loader import dp, bot
from states.state_payment import StorageQiwi
from utils import send_all_admin, clear_firstname, get_dates
from utils.db_api.sqlite import update_userx, get_refillx, add_refillx


###################################################################################
############################## ВВОД СУММЫ ПОПОЛНЕНИЯ ##############################
# Выбор способа пополнения
@dp.callback_query_handler(text_startswith="user_input", state="*")
async def input_amount(call: CallbackQuery, state: FSMContext):
    check_pass = False
    get_payment = get_paymentx()
    if get_payment[5] == "True":
        if get_payment[0] != "None" and get_payment[1] != "None" and get_payment[2] != "None":
            try:
                request = requests.Session()
                request.headers["authorization"] = "Bearer " + get_payment[1]
                response_qiwi = request.get(
                    f"https://edge.qiwi.com/payment-history/v2/persons/{get_payment[0]}/payments",
                    params={"rows": 1, "operation": "IN"})
                if response_qiwi.status_code == 200:
                    pay_amount = int(call.data.split(":")[1])
                    min_input_qiwi = 1  # Минимальная сумма пополнения в рублях
                    get_payments = get_paymentx()
                    if get_payments[0] != "None" or get_payments[1] != "None" or get_payments[2] != "None":
                        try:
                            request = requests.Session()
                            request.headers["authorization"] = "Bearer " + get_payments[1]
                            response_qiwi = request.get(
                                f"https://edge.qiwi.com/payment-history/v2/persons/{get_payments[0]}/payments",
                                params={"rows": 1, "operation": "IN"})
                            if pay_amount >= min_input_qiwi:
                                passwd = list("1234567890ABCDEFGHIGKLMNOPQRSTUVYXWZ")
                                random.shuffle(passwd)
                                random_chars = "".join([random.choice(passwd) for x in range(10)])
                                generate_number_check = str(random.randint(100000000000, 999999999999))
                                if get_payments[4] == "form":
                                    qiwi = QiwiP2P(get_payments[2])
                                    bill = qiwi.bill(bill_id=generate_number_check, amount=pay_amount,
                                                     comment=generate_number_check)
                                    way_pay = "Form"
                                    delete_msg = await bot.send_message(call.from_user.id, "🥝Платёж был создан.",
                                                                  reply_markup=check_user_out_func(call.from_user.id), parse_mode='HTML')
                                    send_requests = bill.pay_url
                                    send_message = f"""
🌐 Ссылка для оплаты: {send_requests}
Перейдите по ней, и оплатите счет на {pay_amount}. В течении 10 минут..

🔄 После оплаты, нажмите на Проверить оплату"""
                                await call.message.edit_text(send_message,
                                                     reply_markup=create_pay_qiwi_func(send_requests,
                                                                                       generate_number_check,
                                                                                       delete_msg.message_id,
                                                                                       way_pay), parse_mode='HTML')
                                await state.finish()
                            else:
                                await StorageQiwi.here_input_qiwi_amount.set()
                                await message.answer(f"❌ <b>Неверная сумма пополнения</b>\n"
                                                     f"▶ Мин. сумма пополнения: <code>{min_input_qiwi}руб</code>\n"
                                                     f"💵 Введите сумму для пополнения средств 🥝", parse_mode='HTML')
                        except json.decoder.JSONDecodeError or UnicodeEncodeError:
                            await state.finish()
                            await message.answer("❕ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                                                 "⌛ Попробуйте чуть позже.",
                                                 reply_markup=check_user_out_func(message.from_user.id), parse_mode='HTML')
                            await send_all_admin("<b>🥝 QIWI кошелёк отсутствует</b> ❌\n"
                                                 f"❕ <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>"
                                                 " пытался пополнить баланс\n"
                                                 "❗ Как можно быстрее замените QIWI кошелёк", parse_mode='HTML')
                    else:
                        await state.finish()
                        await bot.delete_message(message.chat.id, del_msg.message_id)
                        await message.answer("❕ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                                             "⌛ Попробуйте чуть позже.",
                                             reply_markup=check_user_out_func(message.from_user.id), parse_mode='HTML')
                        await send_all_admin("<b>🥝 QIWI кошелёк отсутствует</b> ❌\n"
                                             f"❕ <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>"
                                             " пытался пополнить баланс\n"
                                             "❗ Как можно быстрее замените QIWI кошелёк", parse_mode='HTML')
                else:
                    check_pass = True
            except json.decoder.JSONDecodeError:
                check_pass = True

            if check_pass:
                await bot.answer_callback_query(call.id, "❗ Пополнение временно недоступно", parse_mode='HTML')
                await send_all_admin(
                    f"👤 Пользователь <a href='tg://user?id={call.from_user.id}'>{clear_firstname(call.from_user.first_name)}</a> "
                    f"пытался пополнить баланс.\n"
                    f"<b>❌ QIWI кошелёк не работает. Срочно замените его.</b>", parse_mode='HTML')
        else:
            await bot.answer_callback_query(call.id, "❗ Пополнение временно недоступно")
            await send_all_admin(
                f"👤 Пользователь <a href='tg://user?id={call.from_user.id}'>{clear_firstname(call.from_user.first_name)}</a> "
                f"пытался пополнить баланс.\n"
                f"<b>❌ QIWI кошелёк недоступен. Срочно замените его.</b>")
    else:
        await bot.answer_callback_query(call.id, "❗ Пополнения в боте временно отключены")


###################################################################################
####################################### QIWI ######################################
# Обработка колбэка "Проверить оплату" QIWI через Форму
@dp.callback_query_handler(text_startswith="Pay:Form:")
async def check_qiwi_pay(call: CallbackQuery):
    receipt = int(call.data[9:].split(":")[0])
    message_id = call.data[9:].split(":")[1]
    get_payments = get_paymentx()
    get_user_info = get_userx(user_id=call.from_user.id)
    if get_payments[0] != "None" or get_payments[1] != "None" or get_payments[2] != "None":
        qiwi = QiwiP2P(get_payments[2])
        pay_comment = qiwi.check(bill_id=receipt).comment  # Получение комментария платежа
        pay_status = qiwi.check(bill_id=receipt).status  # Получение статуса платежа
        pay_amount = float(qiwi.check(bill_id=receipt).amount)  # Получение суммы платежа в рублях
        pay_amount = int(pay_amount)
        if pay_status == "PAID":
            get_purchase = get_refillx("*", receipt=receipt)
            if get_purchase is None:

                add_refillx(call.from_user.id, "🥝Киви", call.from_user.first_name, pay_comment,
                            pay_amount, receipt, "Form", get_dates(),
                            int(time.time()))

                # Обновление баланса у пользователя
                update_userx(call.from_user.id,
                             balance=int(get_user_info[4]) + pay_amount)
                await call.message.delete()
                await bot.send_message(call.from_user.id, f"""💵 Ваш баланс был пополнен на {pay_amount} руб.
💰 Вы можете обменять на голду""",                               
                                          reply_markup=check_user_out_func(call.from_user.id), parse_mode='HTML')
            else:
                await bot.answer_callback_query(call.id, "❗ Ваше пополнение уже зачислено.")
        elif pay_status == "EXPIRED":
            await bot.edit_message_text("<b>❌ Время оплаты вышло. Платёж был удалён.</b>",
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=check_user_out_func(call.from_user.id), parse_mode='HTML')
        elif pay_status == "WAITING":
            await bot.answer_callback_query(call.id, "❗ Оплата не была произведена.")
        elif pay_status == "REJECTED":
            await bot.edit_message_text("<b>❌ Счёт был отклонён.</b>",
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=check_user_out_func(call.from_user.id), parse_mode='HTML')
    else:
        await send_all_admin("<b>❗ Кто-то пытался проверить платёж, но QIWI не работает\n"
                             "❗ Срочно замените QIWI данные</b>", parse_mode='HTML')
        await bot.answer_callback_query(call.id, "❗ Извиняемся за доставленные неудобства,\n"
                                                 "проверка платежа временно недоступна.\n"
                                                 "⏳ Попробуйте чуть позже.")


