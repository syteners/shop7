# - *- coding: utf- 8 - *-
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.database.db_settings import Settingsx
from tgbot.database.db_users import Userx
from tgbot.keyboards.inline_admin import turn_open_finl, settings_open_finl, stars_markup_finl, required_channels_finl
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import send_admins, insert_tags
from tgbot.data.config import get_required_channels, add_required_channel, remove_required_channel

router = Router(name=__name__)


# Изменение данных
@router.message(F.text == "🖍 Изменить данные")
async def settings_data_edit(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer(
        "<b>🖍 Изменение данных бота.</b>",
        reply_markup=settings_open_finl(),
    )


# Выключатели бота
@router.message(F.text == "🕹 Выключатели")
async def settings_turn_edit(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer(
        "<b>🕹 Включение и выключение основных функций</b>",
        reply_markup=turn_open_finl(),
    )


################################## ВЫКЛЮЧАТЕЛИ #################################
# Включение/выключение тех работ
@router.callback_query(F.data.startswith("turn_work:"))
async def settings_turn_work(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_status = call.data.split(":")[1]

    get_user = Userx.get(user_id=call.from_user.id)
    Settingsx.update(status_work=get_status)

    if get_status == "True":
        send_text = "🔴 Отправил бота на технические работы."
    else:
        send_text = "🟢 Вывел бота из технических работ."

    await send_admins(
        bot,
        f"👤 Администратор <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
        f"{send_text}",
        not_me=get_user.user_id,
    )

    await call.message.edit_reply_markup(reply_markup=turn_open_finl())


# Включение/выключение покупок
@router.callback_query(F.data.startswith("turn_buy:"))
async def settings_turn_buy(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_status = call.data.split(":")[1]

    get_user = Userx.get(user_id=call.from_user.id)
    Settingsx.update(status_buy=get_status)

    if get_status == "True":
        send_text = "🟢 Включил покупки в боте."
    else:
        send_text = "🔴 Выключил покупки в боте."

    await send_admins(
        bot,
        f"👤 Администратор <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
        f"{send_text}",
        not_me=get_user.user_id,
    )

    await call.message.edit_reply_markup(reply_markup=turn_open_finl())


# Включение/выключение пополнений
@router.callback_query(F.data.startswith("turn_pay:"))
async def settings_turn_pay(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_status = call.data.split(":")[1]

    get_user = Userx.get(user_id=call.from_user.id)
    Settingsx.update(status_refill=get_status)

    if get_status == "True":
        send_text = "🟢 Включил пополнения в боте."
    else:
        send_text = "🔴 Выключил пополнения в боте."

    await send_admins(
        bot,
        f"👤 Администратор <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
        f"{send_text}",
        not_me=get_user.user_id,
    )

    await call.message.edit_reply_markup(reply_markup=turn_open_finl())


############################### ИЗМЕНЕНИЕ ДАННЫХ ###############################
# Изменение поддержки
@router.callback_query(F.data == "settings_edit_support")
async def settings_support_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await state.set_state("here_settings_support")
    await call.message.edit_text(
        "<b>☎️ Отправьте юзернейм для поддержки.</b>\n"
        "❕ Юзернейм пользователя/бота/канала/чата.",
    )


# Изменение FAQ
@router.callback_query(F.data == "settings_edit_faq")
async def settings_faq_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await state.set_state("here_settings_faq")
    await call.message.edit_text(
        "<b>❔ Введите новый текст для FAQ</b>\n"
        "❕ Вы можете использовать заготовленный синтаксис и HTML разметку:\n"
        "▶️ <code>{username}</code>  - логин пользоваля\n"
        "▶️ <code>{user_id}</code>   - айди пользователя\n"
        "▶️ <code>{firstname}</code> - имя пользователя",
    )


################################ ПРИНЯТИЕ ДАННЫХ ###############################
# Принятие поддержки
@router.message(F.text, StateFilter("here_settings_support"))
async def settings_support_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    get_support = message.text

    if get_support.startswith("@"):
        get_support = get_support[1:]

    await state.clear()

    Settingsx.update(misc_support=get_support)

    await message.answer(
        "<b>🖍 Изменение данных бота.</b>",
        reply_markup=settings_open_finl(),
    )


# Принятие FAQ
@router.message(F.text, StateFilter("here_settings_faq"))
async def settings_faq_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    get_message = insert_tags(message.from_user.id, message.text)

    try:
        await (await message.answer(get_message)).delete()
    except:
        return await message.answer(
            "<b>❌ Ошибка синтаксиса HTML.</b>\n"
            "❔ Введите новый текст для FAQ",
        )

    await state.clear()
    Settingsx.update(misc_faq=message.text)

    await message.answer(
        "<b>🖍 Изменение данных бота.</b>",
        reply_markup=settings_open_finl(),
    )


################################################################################
############################### НАЦЕНКА НА ЗВЕЗДЫ ##############################
# Наценка на звезды
@router.message(F.text == "⭐ Наценка на звезды")
async def stars_markup_menu(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_settings = Settingsx.get()

    await message.answer(
        f"<b>⭐ Настройка наценки на звезды Telegram</b>\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"▪️ Текущая наценка: <code>{get_settings.stars_markup}%</code>\n"
        f"▪️ При покупке звезд, бот автоматически добавляет наценку к стоимости\n"
        f"▪️ Разница остается на балансе CryptoBot как ваша комиссия\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"<i>Пример: при наценке 10%, если звезды стоят 100$, пользователь заплатит 110$</i>",
        reply_markup=stars_markup_finl(),
    )


# Изменение наценки на звезды
@router.callback_query(F.data == "stars_markup_edit")
async def stars_markup_edit(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.set_state("here_stars_markup")
    await call.message.edit_text(
        "<b>⭐ Введите новый процент наценки на звезды</b>\n"
        "▪️ Введите число от 0 до 100\n"
        "▪️ Пример: <code>10</code> - наценка 10%\n"
        "▪️ <code>0</code> - без наценки (не рекомендуется)",
    )


# Принятие наценки на звезды
@router.message(F.text, StateFilter("here_stars_markup"))
async def stars_markup_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    try:
        markup_value = int(message.text.strip())
        
        if markup_value < 0 or markup_value > 100:
            return await message.answer(
                "<b>❌ Ошибка! Наценка должна быть от 0 до 100%</b>\n"
                "⭐ Введите новый процент наценки на звезды"
            )
        
        old_markup = Settingsx.get().stars_markup
        await state.clear()
        
        Settingsx.update(stars_markup=markup_value)
        
        get_user = Userx.get(user_id=message.from_user.id)
        
        await send_admins(
            bot,
            f"👤 Администратор <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
            f"⭐ Изменил наценку на звезды: {old_markup}% → {markup_value}%",
            not_me=get_user.user_id,
        )
        
        await message.answer(
            f"<b>✅ Наценка на звезды успешно изменена!</b>\n"
            f"▪️ Старая наценка: <code>{old_markup}%</code>\n"
            f"▪️ Новая наценка: <code>{markup_value}%</code>",
            reply_markup=stars_markup_finl(),
        )
        
    except ValueError:
        await message.answer(
            "<b>❌ Ошибка! Введите корректное число</b>\n"
            "⭐ Введите новый процент наценки на звезды"
        )


################################################################################
########################## ОБЯЗАТЕЛЬНАЯ ПОДПИСКА ################################
# Меню управления обязательной подпиской
@router.message(F.text == "📢 Обязательная подписка")
async def required_channels_menu(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()
    
    channels = get_required_channels()
    channels_count = len(channels)
    
    await message.answer(
        f"<b>📢 Управление обязательной подпиской</b>\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"▪️ Добавлено каналов: <code>{channels_count}/5</code>\n"
        f"▪️ Пользователи должны подписаться на все указанные каналы\n"
        f"▪️ Администраторы автоматически обходят проверку\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"<i>Для добавления канала нужен его ID (например: -1001234567890)</i>",
        reply_markup=required_channels_finl(),
    )


# Добавление канала
@router.callback_query(F.data == "channel_add")
async def channel_add_handler(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    channels = get_required_channels()
    
    if len(channels) >= 5:
        await call.answer("❌ Максимум 5 каналов!", show_alert=True)
        return
    
    await state.set_state("here_channel_add")
    await call.message.edit_text(
        "<b>📢 Добавление обязательного канала</b>\n"
        "➖➖➖➖➖➖➖➖➖➖\n"
        "▪️ Отправьте ID канала или чата\n"
        "▪️ ID должен начинаться с <code>-100</code>\n"
        "▪️ Пример: <code>-1001234567890</code>\n"
        "➖➖➖➖➖➖➖➖➖➖\n"
        "<i>💡 Как получить ID канала:</i>\n"
        "1️⃣ Добавьте бота @userinfobot в канал\n"
        "2️⃣ Перешлите любое сообщение из канала боту\n"
        "3️⃣ Бот покажет ID канала",
    )


# Принятие ID канала
@router.message(F.text, StateFilter("here_channel_add"))
async def channel_add_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    try:
        channel_id = int(message.text.strip())
        
        if not str(channel_id).startswith("-100"):
            return await message.answer(
                "<b>❌ Ошибка! ID канала должен начинаться с -100</b>\n"
                "📢 Отправьте корректный ID канала"
            )
        
        success = add_required_channel(channel_id)
        
        if not success:
            return await message.answer(
                "<b>❌ Ошибка!</b>\n"
                "▪️ Этот канал уже добавлен или достигнут лимит (5 каналов)\n"
                "📢 Отправьте другой ID канала"
            )
        
        await state.clear()
        
        get_user = Userx.get(user_id=message.from_user.id)
        
        await send_admins(
            bot,
            f"👤 Администратор <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
            f"📢 Добавил обязательный канал: <code>{channel_id}</code>",
            not_me=get_user.user_id,
        )
        
        channels = get_required_channels()
        
        await message.answer(
            f"<b>✅ Канал успешно добавлен!</b>\n"
            f"▪️ ID канала: <code>{channel_id}</code>\n"
            f"▪️ Всего каналов: <code>{len(channels)}/5</code>",
            reply_markup=required_channels_finl(),
        )
        
    except ValueError:
        await message.answer(
            "<b>❌ Ошибка! Введите корректное число</b>\n"
            "📢 Отправьте ID канала"
        )


# Удаление канала
@router.callback_query(F.data.startswith("channel_remove:"))
async def channel_remove_handler(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    channel_id = int(call.data.split(":")[1])
    
    success = remove_required_channel(channel_id)
    
    if not success:
        await call.answer("❌ Ошибка при удалении канала!", show_alert=True)
        return
    
    get_user = Userx.get(user_id=call.from_user.id)
    
    await send_admins(
        bot,
        f"👤 Администратор <a href='tg://user?id={get_user.user_id}'>{get_user.user_name}</a>\n"
        f"🗑 Удалил обязательный канал: <code>{channel_id}</code>",
        not_me=get_user.user_id,
    )
    
    channels = get_required_channels()
    
    await call.message.edit_text(
        f"<b>📢 Управление обязательной подпиской</b>\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"▪️ Добавлено каналов: <code>{len(channels)}/5</code>\n"
        f"▪️ Пользователи должны подписаться на все указанные каналы\n"
        f"▪️ Администраторы автоматически обходят проверку\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"✅ Канал <code>{channel_id}</code> удален!",
        reply_markup=required_channels_finl(),
    )
    
    await call.answer("✅ Канал удален!")
