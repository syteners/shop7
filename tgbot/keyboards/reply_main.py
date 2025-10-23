# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from tgbot.data.config import get_admins
from tgbot.utils.const_functions import rkb


# Кнопки главного меню
def menu_frep(user_id) -> ReplyKeyboardMarkup:
    from tgbot.data.config import get_chat_url, get_games_url, get_free_gifts_url
    
    keyboard = ReplyKeyboardBuilder()
    
    chat_url = get_chat_url()
    games_url = get_games_url()
    free_gifts_url = get_free_gifts_url()

    if free_gifts_url and games_url:
        keyboard.row(
            rkb("⭐ Купить звезды"), rkb("🎁 Бесплатные подарки и звезды")
        )
        keyboard.row(
            rkb("🎁 Купить"), rkb("🎮 Игры на звезды")
        )
    elif free_gifts_url:
        keyboard.row(
            rkb("⭐ Купить звезды"), rkb("🎁 Бесплатные подарки и звезды")
        )
        keyboard.row(
            rkb("🎁 Купить")
        )
    elif games_url:
        keyboard.row(
            rkb("⭐ Купить звезды")
        )
        keyboard.row(
            rkb("🎁 Купить"), rkb("🎮 Игры на звезды")
        )
    else:
        keyboard.row(
            rkb("⭐ Купить звезды")
        )
        keyboard.row(
            rkb("🎁 Купить")
        )

    keyboard.row(
        rkb("👤 Профиль"), rkb("🧮 Наличие товаров"),
    )
    
    keyboard.row(
        rkb("🎟️ Промокод"), rkb("🎁 Бонус")
    )
    
    # Добавляем кнопку Чат, если ссылка указана
    if chat_url:
        keyboard.row(
            rkb("💬 Чат"), rkb("☎️ Поддержка"), rkb("❔ FAQ")
        )
    else:
        keyboard.row(
            rkb("☎️ Поддержка"), rkb("❔ FAQ")
        )

    if user_id in get_admins():
        keyboard.row(
            rkb("🎁 Управление товарами"), rkb("📊 Статистика"),
        ).row(
            rkb("⚙️ Настройки"), rkb("🔆 Общие функции"), rkb("🔑 Платежные системы"),
        )

    return keyboard.as_markup(resize_keyboard=True)


# Кнопки платежных систем
def payments_frep() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.row(
        rkb("🔮 ЮMoney"), rkb("🥝 QIWI"),
    ).row(
        rkb("💎 CryptoBot"), rkb("🖲 Способы пополнений")
    ).row(
        rkb("🔙 Главное меню")
    )

    return keyboard.as_markup(resize_keyboard=True)


# Кнопки общих функций
def functions_frep() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.row(
        rkb("🔍 Поиск"), rkb("📢 Рассылка"),
    ).row(
        rkb("🔙 Главное меню")
    )

    return keyboard.as_markup(resize_keyboard=True)


# Кнопки настроек
def settings_frep() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.row(
        rkb("🖍 Изменить данные"), rkb("🕹 Выключатели"),
    ).row(
        rkb("⭐ Наценка на звезды"), rkb("🎟️ Промокоды"),
    ).row(
        rkb("📢 Обязательная подписка")
    ).row(
        rkb("🔙 Главное меню")
    )

    return keyboard.as_markup(resize_keyboard=True)


# Кнопки изменения товаров
def items_frep() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.row(
        rkb("📁 Создать позицию ➕"), rkb("🗃 Создать категорию ➕"),
    ).row(
        rkb("📁 Изменить позицию 🖍"), rkb("🗃 Изменить категорию 🖍")
    ).row(
        rkb("🔙 Главное меню"), rkb("🎁 Добавить товары ➕"), rkb("❌ Удаление")
    )

    return keyboard.as_markup(resize_keyboard=True)
