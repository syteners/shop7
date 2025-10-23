# - *- coding: utf- 8 - *-
import asyncio

from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.data.config import BOT_VERSION, get_desc
from tgbot.database.db_purchases import Purchasesx
from tgbot.database.db_settings import Settingsx
from tgbot.keyboards.inline_user import user_support_finl
from tgbot.keyboards.inline_user_page import *
from tgbot.utils.const_functions import ded, del_message, convert_date
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc_functions import upload_text, insert_tags, get_items_available
from tgbot.utils.text_functions import open_profile_user

router = Router(name=__name__)


# Открытие товаров
@router.message(F.text == "🎁 Купить")
async def user_shop(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_categories = Categoryx.get_all()

    if len(get_categories) >= 1:
        await message.answer(
            "<b>🎁 Выберите нужный вам товар:</b>",
            reply_markup=prod_item_category_swipe_fp(0),
        )
    else:
        await message.answer("<b>🎁 Увы, товары в данное время отсутствуют.</b>")


# Открытие профиля
@router.message(F.text == "👤 Профиль")
async def user_profile(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await open_profile_user(bot, message.from_user.id)


# Проверка товаров в наличии
@router.message(F.text == "🧮 Наличие товаров")
async def user_available(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    items_available = get_items_available()

    await message.answer(
        items_available[0],
        reply_markup=prod_available_swipe_fp(0, len(items_available)),
    )


# Открытие FAQ
@router.message(F.text.in_(('❔ FAQ', '/faq')))
async def user_faq(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_settings = Settingsx.get()
    send_message = get_settings.misc_faq

    if send_message == "None":
        send_message = ded(f"""
            ❔ Информация. Измените её в настройках бота.
            ➖➖➖➖➖➖➖➖➖➖
            {get_desc()}
        """)

    await message.answer(
        insert_tags(message.from_user.id, send_message),
        disable_web_page_preview=True,
    )


# Открытие сообщения с ссылкой на поддержку
@router.message(F.text.in_(('☎️ Поддержка', '/support')))
async def user_support(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_settings = Settingsx.get()

    if get_settings.misc_support == "None":
        return await message.answer(
            ded(f"""
                ☎️ Поддержка. Измените её в настройках бота.
                ➖➖➖➖➖➖➖➖➖➖
                {get_desc()}
            """),
            disable_web_page_preview=True,
        )

    await message.answer(
        "<b>☎️ Нажмите кнопку ниже для связи с Администратором.</b>",
        reply_markup=user_support_finl(get_settings.misc_support),
    )


# Открытие чата
@router.message(F.text == '💬 Чат')
async def user_chat(message: Message, bot: Bot, state: FSM, arSession: ARS):
    from tgbot.data.config import get_chat_url
    from tgbot.keyboards.inline_user import chat_link_finl
    
    await state.clear()
    
    chat_url = get_chat_url()
    
    if not chat_url:
        return await message.answer(
            "<b>💬 Чат не настроен.</b>\n"
            "Попросите администратора указать ссылку на чат в настройках."
        )
    
    # Форматируем ссылку для отображения
    if chat_url.startswith('@'):
        display_url = f"https://t.me/{chat_url[1:]}"
    elif chat_url.startswith('https://'):
        display_url = chat_url
    else:
        display_url = f"https://t.me/{chat_url}"


# Открытие канала с играми
@router.message(F.text == '🎮 Игры на звезды')
async def user_games_channel(message: Message, bot: Bot, state: FSM):
    from tgbot.data.config import get_games_url
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    await state.clear()
    
    games_url = get_games_url()
    
    if not games_url:
        return await message.answer(
            "<b>🎮 Канал с играми не настроен.</b>\n"
            "Попросите администратора указать ссылку в настройках."
        )
    
    if games_url.startswith('@'):
        display_url = f"https://t.me/{games_url[1:]}"
    elif games_url.startswith('https://'):
        display_url = games_url
    else:
        display_url = f"https://t.me/{games_url}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Перейти в канал", url=display_url)]
    ])
    
    await message.answer(
        "<b>🎮 Игры на звезды</b>\n\n"
        "Переходите в наш канал с играми на звезды Telegram!",
        reply_markup=keyboard
    )


# Открытие канала с подарками
@router.message(F.text == '🎁 Бесплатные подарки и звезды')
async def user_gifts_channel(message: Message, bot: Bot, state: FSM):
    from tgbot.data.config import get_free_gifts_url
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    await state.clear()
    
    gifts_url = get_free_gifts_url()
    
    if not gifts_url:
        return await message.answer(
            "<b>🎁 Канал с подарками не настроен.</b>\n"
            "Попросите администратора указать ссылку в настройках."
        )
    
    if gifts_url.startswith('@'):
        display_url = f"https://t.me/{gifts_url[1:]}"
    elif gifts_url.startswith('https://'):
        display_url = gifts_url
    else:
        display_url = f"https://t.me/{gifts_url}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Перейти в канал", url=display_url)]
    ])
    
    await message.answer(
        "<b>🎁 Бесплатные подарки и звезды</b>\n\n"
        "Переходите в наш канал и получайте бесплатные подарки и звезды!",
        reply_markup=keyboard
    )


# Получение ежедневного бонуса
@router.message(F.text == '🎁 Бонус')
async def user_daily_bonus(message: Message, bot: Bot, state: FSM, arSession: ARS):
    import random
    from tgbot.database.db_users import Userx
    from tgbot.utils.const_functions import get_unix
    
    await state.clear()
    
    user_id = message.from_user.id
    get_user = Userx.get(user_id=user_id)
    
    if not get_user:
        return await message.answer("<b>❌ Ошибка: пользователь не найден</b>")
    
    current_time = get_unix()
    time_since_last_bonus = current_time - get_user.user_last_bonus
    
    # Проверяем, прошло ли 24 часа (86400 секунд)
    if time_since_last_bonus < 86400 and get_user.user_last_bonus != 0:
        remaining_time = 86400 - time_since_last_bonus
        hours = remaining_time // 3600
        minutes = (remaining_time % 3600) // 60
        
        return await message.answer(
            f"<b>⏳ Ежедневный бонус уже получен!</b>\n\n"
            f"Следующий бонус будет доступен через: <code>{hours}ч {minutes}мин</code>"
        )
    
    # Генерируем случайный бонус от 0.50$ до 1.00$
    bonus_amount = round(random.uniform(0.50, 1.00), 2)
    
    # Зачисляем бонус на баланс
    new_balance = get_user.user_balance + bonus_amount
    Userx.update(user_id, user_balance=new_balance, user_last_bonus=current_time)
    
    await message.answer(
        f"<b>🎉 Поздравляем!</b>\n\n"
        f"Вы получили ежедневный бонус: <code>${bonus_amount}</code>\n"
        f"💰 Ваш баланс: <code>${new_balance:.2f}</code>\n\n"
        f"<i>Возвращайтесь завтра за новым бонусом!</i>"
    )


# Получение версии бота
@router.message(Command(commands=['version']))
async def admin_version(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer(f"<b>❇️ Текущая версия бота: <code>{BOT_VERSION}</code></b>")


# Получение информации о боте
@router.message(Command(commands=['dj_desc']))
async def admin_desc(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer(get_desc(), disable_web_page_preview=True)


################################################################################
# Возвращение к профилю
@router.callback_query(F.data == "user_profile")
async def user_profile_return(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await del_message(call.message)
    await open_profile_user(bot, call.from_user.id)


# Просмотр истории покупок
@router.callback_query(F.data == "user_purchases")
async def user_purchases(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    get_purchases = Purchasesx.gets(user_id=call.from_user.id)
    get_purchases = get_purchases[-5:]

    if len(get_purchases) >= 1:
        await call.answer("🎁 Последние 5 покупок")
        await del_message(call.message)

        for purchase in get_purchases:
            link_items = await upload_text(arSession, purchase.purchase_data)

            await call.message.answer(
                ded(f"""
                    <b>🧾 Чек: <code>#{purchase.purchase_receipt}</code></b>
                    ▪️ Товар: <code>{purchase.purchase_position_name} | {purchase.purchase_count}шт | {purchase.purchase_price}$</code>
                    ▪️ Дата покупки: <code>{convert_date(purchase.purchase_unix)}</code>
                    ▪️ Товары: <a href='{link_items}'>кликабельно</a>
                """)
            )

            await asyncio.sleep(0.2)

        await open_profile_user(bot, call.from_user.id)
    else:
        await call.answer("❗ У вас отсутствуют покупки", True)


# Страницы наличия товаров
@router.callback_query(F.data.startswith("user_available_swipe:"))
async def user_available_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    remover = int(call.data.split(":")[1])

    items_available = get_items_available()

    if remover >= len(items_available):
        remover = len(items_available) - 1
    if remover < 0:
        remover = 0

    await call.message.edit_text(
        items_available[remover],
        reply_markup=prod_available_swipe_fp(remover, len(items_available)),
    )


################################################################################
# Покупка звезд Telegram
@router.message(F.text == "⭐ Купить звезды")
async def user_buy_stars(message: Message, bot: Bot, state: FSM, arSession: ARS):
    from tgbot.keyboards.inline_user import stars_package_finl
    
    await state.clear()

    get_settings = Settingsx.get()
    STAR_RATE = 0.018
    
    await message.answer(
        ded(f"""
            <b>⭐ Покупка звезд Telegram</b>
            ➖➖➖➖➖➖➖➖➖➖
            ▪️ Выберите пакет звезд для покупки
            ▪️ Минимум: <code>50 звезд</code>
            ▪️ Курс: <code>1 звезда ≈ ${STAR_RATE}</code>
            ▪️ Текущая наценка: <code>{get_settings.stars_markup}%</code>
            ➖➖➖➖➖➖➖➖➖➖
            <i>Пример: 100 звезд = ${100 * STAR_RATE:.2f}
            С наценкой {get_settings.stars_markup}%: ${100 * STAR_RATE * (1 + get_settings.stars_markup / 100):.2f}</i>
        """),
        reply_markup=stars_package_finl()
    )


# Обработка выбора пакета звезд
@router.callback_query(F.data.startswith("stars_package:"))
async def stars_package_select(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    from tgbot.keyboards.inline_user import stars_recipient_finl, stars_package_finl
    
    package = call.data.split(":")[1]
    
    if package == "custom":
        await state.set_state("here_stars_custom_amount")
        await call.message.edit_text(
            ded(f"""
                <b>⭐ Ввод количества звезд</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Введите количество звезд для покупки
                ▪️ Минимум: <code>50 звезд</code>
                ▪️ Максимум: <code>10 000 звезд</code>
                ➖➖➖➖➖➖➖➖➖➖
                <i>Напишите число звезд в ответном сообщении</i>
            """)
        )
    else:
        amount_stars = int(package)
        await call.message.edit_text(
            ded(f"""
                <b>⭐ Выбран пакет: {amount_stars} звезд</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Кому отправить звезды?
            """),
            reply_markup=stars_recipient_finl(amount_stars)
        )


# Обработка пользовательского ввода количества звезд
@router.message(F.text, StateFilter("here_stars_custom_amount"))
async def stars_custom_amount_get(message: Message, bot: Bot, state: FSM, arSession: ARS):
    from tgbot.keyboards.inline_user import stars_recipient_finl, stars_package_finl
    from tgbot.utils.const_functions import is_number, to_number
    
    if not is_number(message.text):
        return await message.answer(
            "<b>❌ Ошибка! Введите корректное число звезд</b>\n"
            "⭐ Пример: <code>100</code>"
        )
    
    amount_stars = int(to_number(message.text))
    
    if amount_stars < 50:
        return await message.answer(
            "<b>❌ Минимальное количество звезд: 50</b>\n"
            "⭐ Введите количество от 50 до 10 000 звезд"
        )
    
    if amount_stars > 10_000:
        return await message.answer(
            "<b>❌ Максимальное количество звезд: 10 000</b>\n"
            "⭐ Введите количество от 50 до 10 000 звезд"
        )
    
    await state.clear()
    await message.answer(
        ded(f"""
            <b>⭐ Выбрано: {amount_stars} звезд</b>
            ➖➖➖➖➖➖➖➖➖➖
            ▪️ Кому отправить звезды?
        """),
        reply_markup=stars_recipient_finl(amount_stars)
    )


# Возврат к выбору пакетов
@router.callback_query(F.data == "stars_back_to_packages")
async def stars_back_to_packages(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    from tgbot.keyboards.inline_user import stars_package_finl
    
    await state.clear()
    get_settings = Settingsx.get()
    STAR_RATE = 0.018
    
    await call.message.edit_text(
        ded(f"""
            <b>⭐ Покупка звезд Telegram</b>
            ➖➖➖➖➖➖➖➖➖➖
            ▪️ Выберите пакет звезд для покупки
            ▪️ Минимум: <code>50 звезд</code>
            ▪️ Курс: <code>1 звезда ≈ ${STAR_RATE}</code>
            ▪️ Текущая наценка: <code>{get_settings.stars_markup}%</code>
            ➖➖➖➖➖➖➖➖➖➖
            <i>Пример: 100 звезд = ${100 * STAR_RATE:.2f}
            С наценкой {get_settings.stars_markup}%: ${100 * STAR_RATE * (1 + get_settings.stars_markup / 100):.2f}</i>
        """),
        reply_markup=stars_package_finl()
    )


# Отмена покупки звезд
@router.callback_query(F.data == "stars_cancel")
async def stars_cancel(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()
    await call.message.delete()
    await call.message.answer("<b>❌ Покупка звезд отменена</b>")


# Проверка подписки на каналы
@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    from tgbot.data.config import get_required_channels, get_admins
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    user_id = call.from_user.id
    
    if user_id in get_admins():
        await call.message.delete()
        await call.message.answer("✅ <b>Добро пожаловать!</b>\n\nВы администратор, проверка подписки не требуется.")
        return
    
    required_channels = get_required_channels()
    
    if not required_channels:
        await call.message.delete()
        await call.message.answer("✅ <b>Добро пожаловать!</b>\n\nПроверка подписки отключена.")
        return
    
    unsubscribed_channels = []
    channel_buttons = []
    
    for channel_id in required_channels:
        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            
            if member.status in ['left', 'kicked']:
                unsubscribed_channels.append(channel_id)
                
                try:
                    chat = await bot.get_chat(channel_id)
                    chat_title = chat.title
                    chat_username = chat.username
                    
                    if chat_username:
                        channel_buttons.append([
                            InlineKeyboardButton(
                                text=f"📢 Подписаться на {chat_title}",
                                url=f"https://t.me/{chat_username}"
                            )
                        ])
                    else:
                        invite_link = await bot.create_chat_invite_link(channel_id)
                        channel_buttons.append([
                            InlineKeyboardButton(
                                text=f"📢 Подписаться на {chat_title}",
                                url=invite_link.invite_link
                            )
                        ])
                except:
                    pass
        except:
            pass
    
    if unsubscribed_channels:
        channel_buttons.append([
            InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subscription")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=channel_buttons)
        
        await call.answer(
            "⚠️ Вы еще не подписались на все каналы!",
            show_alert=True
        )
        
        await call.message.edit_text(
            "⚠️ <b>Для использования бота необходимо подписаться на наши каналы!</b>\n\n"
            "👇 <b>Нажмите на кнопки ниже, чтобы подписаться:</b>\n\n"
            "После подписки на все каналы нажмите кнопку <b>✅ Проверить подписку</b>",
            reply_markup=keyboard
        )
    else:
        from tgbot.keyboards.reply_main import menu_frep
        
        await call.message.delete()
        await call.message.answer(
            "✅ <b>Отлично! Вы подписаны на все каналы!</b>\n\n"
            "Теперь вы можете пользоваться ботом. Используйте меню ниже для выбора действий.\n\n"
            "Или отправьте команду /start",
            reply_markup=menu_frep(user_id)
        )
