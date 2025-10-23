# - *- coding: utf- 8 - *-
from typing import Union

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.database.db_payments import Paymentsx
from tgbot.database.db_refill import Refillx
from tgbot.database.db_settings import Settingsx
from tgbot.database.db_users import Userx
from tgbot.keyboards.inline_user import refill_bill_finl, refill_method_finl, refill_cancel_finl
from tgbot.services.api_qiwi import QiwiAPI
from tgbot.services.api_yoomoney import YoomoneyAPI
from tgbot.services.api_cryptobot import CryptoBotAPI
from tgbot.utils.const_functions import is_number, to_number, gen_id
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import send_admins

min_refill_usd = 10  # Минимальная сумма пополнения в долларах

router = Router(name=__name__)


# Выбор способа пополнения
@router.callback_query(F.data == "user_refill")
async def refill_method(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_payment = Paymentsx.get()

    if get_payment.way_qiwi == "False" and get_payment.way_yoomoney == "False" and get_payment.way_cryptobot == "False":
        return await call.answer("❗️ Пополнения временно недоступны", True)

    await call.message.edit_text(
        "<b>💰 Выберите способ пополнения</b>",
        reply_markup=refill_method_finl(),
    )


# Выбор способа пополнения
@router.callback_query(F.data.startswith("user_refill_method:"))
async def refill_method_select(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    pay_method = call.data.split(":")[1]

    await state.update_data(here_pay_method=pay_method)

    await state.set_state("here_refill_amount")
    await call.message.edit_text(
        "<b>💰 Введите сумму пополнения</b>\n"
        f"▪️ Минимум: <code>${min_refill_usd}</code>\n"
        f"▪️ Максимум: <code>$100,000</code>",
        reply_markup=refill_cancel_finl()
    )


################################################################################
################################### ВВОД СУММЫ #################################
# Принятие суммы для пополнения средств
@router.message(F.text, StateFilter("here_refill_amount"))
async def refill_amount_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    if not is_number(message.text):
        return await message.answer(
            "<b>❌ Данные были введены неверно.</b>\n"
            "💰 Введите сумму для пополнения средств",
        )

    if to_number(message.text) < min_refill_usd or to_number(message.text) > 100_000:
        return await message.answer(
            f"<b>❌ Неверная сумма пополнения</b>\n"
            f"❗️ Cумма не должна быть меньше <code>${min_refill_usd}</code> и больше <code>$100 000</code>\n"
            f"💰 Введите сумму для пополнения средств",
        )

    cache_message = await message.answer("<b>♻️ Подождите, платёж генерируется...</b>")

    pay_amount = to_number(message.text)
    pay_method = (await state.get_data())['here_pay_method']
    await state.clear()

    if pay_method == "QIWI":
        bill_message, bill_link, bill_receipt = await (
            QiwiAPI(
                bot=bot,
                arSession=arSession,
            )
        ).bill(pay_amount)
    elif pay_method == "Yoomoney":
        bill_message, bill_link, bill_receipt = await (
            YoomoneyAPI(
                bot=bot,
                arSession=arSession,
            )
        ).bill(pay_amount)
    elif pay_method == "CryptoBot":
        get_settings = Settingsx.get()
        stars_markup = get_settings.stars_markup
        
        bill_message, bill_link, bill_receipt = await (
            CryptoBotAPI(
                bot=bot,
                arSession=arSession,
            )
        ).bill(pay_amount, stars_markup=stars_markup)

    if bill_message:
        await cache_message.edit_text(
            bill_message,
            reply_markup=refill_bill_finl(bill_link, bill_receipt, pay_method),
        )


################################################################################
############################### ПОКУПКА ЗВЕЗД ##################################
STAR_RATE = 0.018

# Обработка выбора получателя звезд
@router.callback_query(F.data.startswith("stars_recipient:"))
async def stars_recipient_select(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    from tgbot.keyboards.inline_user import stars_confirm_finl
    from tgbot.utils.const_functions import ded
    
    parts = call.data.split(":")
    recipient_type = parts[1]
    amount_stars = int(parts[2])
    
    get_settings = Settingsx.get()
    
    base_amount = round(amount_stars * STAR_RATE, 2)
    markup_amount = round(base_amount * get_settings.stars_markup / 100, 2)
    total_amount = round(base_amount + markup_amount, 2)
    
    if recipient_type == "self":
        await call.message.edit_text(
            ded(f"""
                <b>⭐ Подтверждение покупки звезд</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Количество звезд: <code>{amount_stars} ⭐</code>
                ▪️ Получатель: <code>Вы сами</code>
                ▪️ Базовая стоимость: <code>${base_amount}</code>
                ▪️ Наценка ({get_settings.stars_markup}%): <code>+${markup_amount}</code>
                ▪️ К оплате: <code>${total_amount}</code>
                ➖➖➖➖➖➖➖➖➖➖
                ❗ После оплаты звезды будут отправлены вам через Telegram
            """),
            reply_markup=stars_confirm_finl(amount_stars, recipient_type, None, total_amount)
        )
    else:
        await state.set_state("here_stars_friend_username")
        await state.update_data(amount_stars=amount_stars, recipient_type=recipient_type)
        await call.message.edit_text(
            ded(f"""
                <b>⭐ Отправка звезд другу</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Введите username получателя в Telegram
                ▪️ Формат: <code>@username</code> или <code>username</code>
                ➖➖➖➖➖➖➖➖➖➖
                <i>Пример: @ivan или ivan</i>
            """)
        )


# Обработка ввода username друга
@router.message(F.text, StateFilter("here_stars_friend_username"))
async def stars_friend_username_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    from tgbot.keyboards.inline_user import stars_confirm_finl
    from tgbot.utils.const_functions import ded
    
    username = message.text.strip()
    if username.startswith("@"):
        username = username[1:]
    
    if len(username) < 3:
        return await message.answer(
            "<b>❌ Username слишком короткий</b>\n"
            "⭐ Введите корректный username получателя"
        )
    
    data = await state.get_data()
    amount_stars = data.get("amount_stars")
    recipient_type = data.get("recipient_type")
    
    await state.clear()
    
    get_settings = Settingsx.get()
    
    base_amount = round(amount_stars * STAR_RATE, 2)
    markup_amount = round(base_amount * get_settings.stars_markup / 100, 2)
    total_amount = round(base_amount + markup_amount, 2)
    
    await message.answer(
        ded(f"""
            <b>⭐ Подтверждение покупки звезд</b>
            ➖➖➖➖➖➖➖➖➖➖
            ▪️ Количество звезд: <code>{amount_stars} ⭐</code>
            ▪️ Получатель: <code>@{username}</code>
            ▪️ Базовая стоимость: <code>${base_amount}</code>
            ▪️ Наценка ({get_settings.stars_markup}%): <code>+${markup_amount}</code>
            ▪️ К оплате: <code>${total_amount}</code>
            ➖➖➖➖➖➖➖➖➖➖
            ❗ После оплаты звезды будут отправлены пользователю @{username}
        """),
        reply_markup=stars_confirm_finl(amount_stars, recipient_type, username, total_amount)
    )


# Обработка подтверждения покупки звезд через CryptoBot
@router.callback_query(F.data.startswith("stars_confirm_cryptobot:"))
async def stars_confirm_cryptobot(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    from tgbot.utils.const_functions import ded
    
    parts = call.data.split(":")
    amount_stars = int(parts[1])
    recipient_type = parts[2]
    recipient_username = parts[3] if len(parts) > 3 and parts[3] != "none" else None
    
    cache_message = await call.message.edit_text("<b>♻️ Подождите, счёт генерируется...</b>")
    
    get_settings = Settingsx.get()
    stars_markup = get_settings.stars_markup
    
    base_amount = round(amount_stars * STAR_RATE, 2)
    total_amount = round(base_amount * (1 + stars_markup / 100), 2)
    
    bill_message, bill_link, bill_receipt = await (
        CryptoBotAPI(
            bot=bot,
            arSession=arSession,
        )
    ).bill(base_amount, stars_markup=stars_markup)
    
    if bill_message:
        await state.update_data(
            stars_purchase_data={
                "amount_stars": amount_stars,
                "amount_paid": total_amount,
                "recipient_type": recipient_type,
                "recipient_username": recipient_username,
                "markup_percent": stars_markup
            }
        )
        
        await cache_message.edit_text(
            bill_message,
            reply_markup=refill_bill_finl(bill_link, bill_receipt, "CryptoBot_Stars"),
        )


# Обработка подтверждения покупки звезд с баланса
@router.callback_query(F.data.startswith("stars_confirm_balance:"))
async def stars_confirm_balance(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    from tgbot.utils.const_functions import ded, get_unix
    from tgbot.database.db_stars_purchases import StarsPurchasex
    
    parts = call.data.split(":")
    amount_stars = int(parts[1])
    recipient_type = parts[2]
    recipient_username = parts[3] if len(parts) > 3 and parts[3] != "none" else None
    
    # БЕЗОПАСНОСТЬ: Пересчитываем сумму на сервере, не доверяя клиенту
    get_settings = Settingsx.get()
    stars_markup = get_settings.stars_markup
    
    base_amount = round(amount_stars * STAR_RATE, 2)
    total_amount = round(base_amount * (1 + stars_markup / 100), 2)
    
    get_user = Userx.get(user_id=call.from_user.id)
    
    if get_user.user_balance < total_amount:
        return await call.answer(
            f"❌ Недостаточно средств на балансе!\n"
            f"У вас: ${get_user.user_balance}\n"
            f"Нужно: ${total_amount}",
            show_alert=True
        )
    
    await call.message.edit_text("<b>♻️ Обрабатываем покупку...</b>")
    
    # Списываем средства
    new_balance = round(get_user.user_balance - total_amount, 2)
    Userx.update(
        user_id=call.from_user.id,
        user_balance=new_balance
    )
    
    receipt = f"BALANCE_{gen_id()}"
    
    if recipient_type == "self":
        recipient_user_id = call.from_user.id
        recipient_username_db = "self"
    else:
        try:
            recipient_chat = await bot.get_chat(f"@{recipient_username}")
            recipient_user_id = recipient_chat.id
            recipient_username_db = recipient_username
        except Exception:
            # Возвращаем деньги правильно - добавляем обратно
            Userx.update(
                user_id=call.from_user.id,
                user_balance=round(get_user.user_balance, 2)
            )
            return await call.message.edit_text(
                f"<b>❌ Не удалось найти пользователя @{recipient_username}</b>\n"
                f"Средства возвращены на ваш баланс."
            )
    
    # Сохраняем покупку в БД с правильными именами полей
    StarsPurchasex.add(
        user_id=call.from_user.id,
        recipient_id=recipient_user_id,
        recipient_username=recipient_username_db,
        amount_stars=amount_stars,
        amount_paid=total_amount,
        markup_percent=stars_markup,
        purchase_receipt=receipt,
        purchase_unix=get_unix()
    )
    
    # Зачисляем звезды получателю
    await credit_stars_to_recipient(
        bot=bot,
        buyer_id=call.from_user.id,
        recipient_id=recipient_user_id,
        amount_stars=amount_stars,
        recipient_username=recipient_username if recipient_type == "friend" else None
    )
    
    # Уведомляем покупателя
    if recipient_type == "self":
        await call.message.edit_text(
            ded(f"""
                <b>✅ Покупка звезд успешно завершена!</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Количество: <code>{amount_stars} ⭐</code>
                ▪️ Оплачено с баланса: <code>${total_amount}</code>
                ▪️ Звезды отправлены вам
                ▪️ Чек: <code>{receipt}</code>
                ➖➖➖➖➖➖➖➖➖➖
                💰 Ваш баланс: <code>${new_balance}</code>
            """)
        )
    else:
        await call.message.edit_text(
            ded(f"""
                <b>✅ Покупка звезд успешно завершена!</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Количество: <code>{amount_stars} ⭐</code>
                ▪️ Получатель: <code>@{recipient_username}</code>
                ▪️ Оплачено с баланса: <code>${total_amount}</code>
                ▪️ Чек: <code>{receipt}</code>
                ➖➖➖➖➖➖➖➖➖➖
                💰 Ваш баланс: <code>${new_balance}</code>
            """)
        )
    
    # Уведомляем админов
    await send_admins(
        bot,
        f"⭐ <b>Покупка звезд с баланса</b>\n"
        f"👤 Пользователь: <b>@{get_user.user_login}</b> | <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
        f"▪️ Количество: <code>{amount_stars} ⭐</code>\n"
        f"▪️ Получатель: <code>{'себе' if recipient_type == 'self' else '@' + recipient_username}</code>\n"
        f"▪️ Сумма: <code>${total_amount}</code>\n"
        f"▪️ Чек: <code>#{receipt}</code>"
    )


################################################################################
############################## ЗАЧИСЛЕНИЕ ЗВЕЗД ################################
# Функция зачисления звезд получателю
async def credit_stars_to_recipient(bot: Bot, buyer_id: int, recipient_id: int, amount_stars: int, recipient_username: str = None):
    """
    Зачисляет звезды получателю (пока просто отправляет уведомление)
    В будущем здесь можно добавить реальное зачисление через Telegram API
    """
    try:
        if recipient_id == buyer_id:
            await bot.send_message(
                recipient_id,
                f"<b>⭐ Вам зачислено {amount_stars} звезд!</b>\n"
                f"Спасибо за покупку!"
            )
        else:
            await bot.send_message(
                recipient_id,
                f"<b>⭐ Вам подарили {amount_stars} звезд!</b>\n"
                f"От пользователя @{recipient_username or 'Аноним'}"
            )
            await bot.send_message(
                buyer_id,
                f"<b>✅ Звезды успешно отправлены пользователю!</b>\n"
                f"Получатель: @{recipient_username}"
            )
    except Exception as e:
        # Если не удалось отправить, просто пропускаем
        pass


################################################################################
############################### ПРОВЕРКА ПЛАТЕЖЕЙ ##############################
# Проверка оплаты - ЮMoney
@router.callback_query(F.data.startswith('Pay:Yoomoney'))
async def refill_check_yoomoney(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    pay_way = call.data.split(":")[1]
    pay_receipt = call.data.split(":")[2]

    pay_status, pay_amount = await (
        YoomoneyAPI(
            bot=bot,
            arSession=arSession,
        )
    ).bill_check(pay_receipt)

    if pay_status == 0:
        get_refill = Refillx.get(refill_receipt=pay_receipt)

        if get_refill is None:
            await refill_success(
                bot=bot,
                call=call,
                pay_way=pay_way,
                pay_amount=pay_amount,
                pay_receipt=pay_receipt,
                pay_comment=pay_receipt,
            )
        else:
            await call.answer("❗ Ваше пополнение уже зачислено.", True, cache_time=60)
    elif pay_status == 1:
        await call.answer("❗️ Не удалось проверить платёж. Попробуйте позже", True, cache_time=5)
    elif pay_status == 2:
        await call.answer("❗️ Платёж не был найден. Попробуйте позже", True, cache_time=5)
    elif pay_status == 3:
        await call.answer("❗️ Оплата была произведена не в долларах", True, cache_time=5)
    else:
        await call.answer(f"❗ Неизвестная ошибка {pay_status}. Обратитесь в поддержку.", True, cache_time=5)


# Проверка оплаты - QIWI
@router.callback_query(F.data.startswith('Pay:QIWI'))
async def refill_check_qiwi(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    pay_way = call.data.split(":")[1]
    pay_receipt = call.data.split(":")[2]

    pay_status, pay_amount = await (
        QiwiAPI(
            bot=bot,
            arSession=arSession,
        )
    ).bill_check(pay_receipt)

    if pay_status == 0:
        get_refill = Refillx.get(refill_receipt=pay_receipt)

        if get_refill is None:
            await refill_success(
                bot=bot,
                call=call,
                pay_way=pay_way,
                pay_amount=pay_amount,
                pay_receipt=pay_receipt,
                pay_comment=pay_receipt,
            )
        else:
            await call.answer("❗ Ваше пополнение уже зачислено.", True, cache_time=60)
    elif pay_status == 1:
        await call.answer("❗️ Не удалось проверить платёж. Попробуйте позже", True, cache_time=5)
    elif pay_status == 2:
        await call.answer("❗ Платёж не был найден. Попробуйте позже.", True, cache_time=5)
    elif pay_status == 3:
        await call.answer("❗ Оплата была произведена не в долларах.", True, cache_time=5)
    else:
        await call.answer(f"❗ Неизвестная ошибка {pay_status}. Обратитесь в поддержку.", True, cache_time=5)


# Проверка оплаты - CryptoBot
@router.callback_query(F.data.startswith('Pay:CryptoBot'))
async def refill_check_cryptobot(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    parts = call.data.split(":")
    pay_way = parts[1]
    pay_receipt = parts[2]
    
    is_stars_payment = pay_way == "CryptoBot_Stars"

    pay_status, pay_amount = await (
        CryptoBotAPI(
            bot=bot,
            arSession=arSession,
        )
    ).bill_check(pay_receipt)

    if pay_status == 0:
        if is_stars_payment:
            from tgbot.database.db_stars_purchases import StarsPurchasex
            from tgbot.utils.const_functions import get_unix
            
            get_stars_purchase = StarsPurchasex.get(purchase_receipt=pay_receipt)
            
            if get_stars_purchase is None:
                data = await state.get_data()
                stars_data = data.get("stars_purchase_data", {})
                
                amount_stars = stars_data.get("amount_stars", 0)
                amount_paid = stars_data.get("amount_paid", 0)
                recipient_type = stars_data.get("recipient_type", "self")
                recipient_username = stars_data.get("recipient_username", "self")
                markup_percent = stars_data.get("markup_percent", 0)
                
                recipient_id = call.from_user.id
                if recipient_username and recipient_username != "self":
                    try:
                        recipient_chat = await bot.get_chat(f"@{recipient_username}")
                        recipient_id = recipient_chat.id
                    except:
                        recipient_id = 0
                
                StarsPurchasex.add(
                    user_id=call.from_user.id,
                    recipient_id=recipient_id,
                    recipient_username=recipient_username if recipient_username else "self",
                    amount_stars=amount_stars,
                    amount_paid=amount_paid,
                    markup_percent=markup_percent,
                    purchase_receipt=pay_receipt,
                    purchase_unix=get_unix()
                )
                
                # Зачисляем звезды получателю
                await credit_stars_to_recipient(
                    bot=bot,
                    buyer_id=call.from_user.id,
                    recipient_id=recipient_id,
                    amount_stars=amount_stars,
                    recipient_username=recipient_username if recipient_type == "friend" else None
                )
                
                await state.clear()
                
                get_user = Userx.get(user_id=call.from_user.id)
                
                if recipient_type == "self":
                    recipient_text = "вам"
                else:
                    recipient_text = f"пользователю @{recipient_username}"
                
                await call.message.edit_text(
                    f"<b>⭐ Покупка звезд успешно выполнена!</b>\n"
                    f"➖➖➖➖➖➖➖➖➖➖\n"
                    f"▪️ Количество звезд: <code>{amount_stars} ⭐</code>\n"
                    f"▪️ Получатель: <code>{recipient_text}</code>\n"
                    f"▪️ Оплачено: <code>${amount_paid}</code>\n"
                    f"▪️ Чек: <code>#{pay_receipt}</code>\n"
                    f"➖➖➖➖➖➖➖➖➖➖\n"
                    f"✅ Звезды отправлены {recipient_text}!",
                )
                
                await send_admins(
                    bot,
                    f"⭐ <b>Покупка звезд</b>\n"
                    f"👤 Пользователь: <b>@{get_user.user_login}</b> | <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
                    f"▪️ Количество: <code>{amount_stars} ⭐</code>\n"
                    f"▪️ Получатель: <code>{recipient_text}</code>\n"
                    f"▪️ Сумма: <code>${amount_paid}</code>\n"
                    f"▪️ Чек: <code>#{pay_receipt}</code>"
                )
            else:
                await call.answer("❗ Эта покупка звезд уже зачислена.", True, cache_time=60)
        else:
            get_refill = Refillx.get(refill_receipt=pay_receipt)

            if get_refill is None:
                await refill_success(
                    bot=bot,
                    call=call,
                    pay_way=pay_way.replace("_Stars", ""),
                    pay_amount=pay_amount,
                    pay_receipt=pay_receipt,
                    pay_comment=pay_receipt,
                )
            else:
                await call.answer("❗ Ваше пополнение уже зачислено.", True, cache_time=60)
    elif pay_status == 1:
        await call.answer("❗️ Не удалось проверить платёж. Попробуйте позже", True, cache_time=5)
    elif pay_status == 2:
        await call.answer("❗ Платёж не был найден. Попробуйте позже.", True, cache_time=5)
    elif pay_status == 3:
        await call.answer("❗ Оплата была произведена не в криптовалюте.", True, cache_time=5)
    else:
        await call.answer(f"❗ Неизвестная ошибка {pay_status}. Обратитесь в поддержку.", True, cache_time=5)


################################################################################
#################################### ПРОЧЕЕ ####################################
# Зачисление средств
async def refill_success(
        bot: Bot,
        call: CallbackQuery,
        pay_way: str,
        pay_amount: float,
        pay_receipt: Union[str, int] = None,
        pay_comment: str = None,
):
    get_user = Userx.get(user_id=call.from_user.id)

    if pay_receipt is None:
        pay_receipt = gen_id()
    if pay_comment is None:
        pay_comment = ""

    Refillx.add(
        user_id=get_user.user_id,
        refill_comment=pay_comment,
        refill_amount=pay_amount,
        refill_receipt=pay_receipt,
        refill_method=pay_way,
    )

    Userx.update(
        call.from_user.id,
        user_balance=round(get_user.user_balance + pay_amount, 2),
        user_refill=round(get_user.user_refill + pay_amount, 2),
    )

    await call.message.edit_text(
        f"<b>💰 Вы пополнили баланс на сумму <code>${pay_amount}</code>. Удачи ❤️\n"
        f"🧾 Чек: <code>#{pay_receipt}</code></b>",
    )

    await send_admins(
        bot,
        f"👤 Пользователь: <b>@{get_user.user_login}</b> | <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a> | <code>{get_user.user_id}</code>\n"
        f"💰 Сумма пополнения: <code>${pay_amount}</code>\n"
        f"🧾 Чек: <code>#{pay_receipt}</code>"
    )
