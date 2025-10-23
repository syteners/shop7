# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def promocode_admin_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="➕ Создать промокод", callback_data="admin_create_promocode")],
        [InlineKeyboardButton(text="📋 Список промокодов", callback_data="admin_list_promocodes")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def promocode_usage_type_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="1️⃣ Одноразовый", callback_data="promo_usage:1")],
        [InlineKeyboardButton(text="5️⃣ 5 использований", callback_data="promo_usage:5")],
        [InlineKeyboardButton(text="🔄 Многоразовый (10)", callback_data="promo_usage:10")],
        [InlineKeyboardButton(text="♾️ Безлимитный", callback_data="promo_usage:999999")],
        [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_promocodes")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def promocode_list_keyboard(promocodes, page=0) -> InlineKeyboardMarkup:
    keyboard = []
    
    items_per_page = 5
    start = page * items_per_page
    end = start + items_per_page
    page_items = promocodes[start:end]
    
    for promo in page_items:
        usage_text = f"{promo.usage_count}/{promo.max_usage}"
        if promo.max_usage == 999999:
            usage_text = f"{promo.usage_count}/∞"
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"🎟️ {promo.promocode} | {promo.balance}$ | {usage_text}",
                callback_data=f"promo_info:{promo.promocode}"
            )
        ])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"promo_page:{page-1}"))
    if end < len(promocodes):
        nav_buttons.append(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"promo_page:{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_promocodes")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def promocode_info_keyboard(promocode: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🗑 Удалить промокод", callback_data=f"promo_delete:{promocode}")],
        [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list_promocodes")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
