# - *- coding: utf- 8 - *-
from typing import Union

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.database.db_payments import Paymentsx
from tgbot.utils.const_functions import ikb


################################################################################
#################################### ПРОЧЕЕ ####################################
# Открытие своего профиля
def user_profile_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("💰 Пополнить", data="user_refill"),
        ikb("🎁 Мои покупки", data="user_purchases")
    )

    return keyboard.as_markup()


# Ссылка на поддержку
def user_support_finl(support_login: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("💌 Написать в поддержку", url=f"https://t.me/{support_login}"),
    )

    return keyboard.as_markup()


# Ссылка на чат
def chat_link_finl(chat_url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("💬 Перейти в чат", url=chat_url),
    )

    return keyboard.as_markup()


################################################################################
################################### ПЛАТЕЖИ ####################################
# Выбор способов пополнения
def refill_method_finl() -> Union[InlineKeyboardMarkup, None]:
    keyboard = InlineKeyboardBuilder()

    get_payments = Paymentsx.get()

    if get_payments.way_qiwi == "True":
        keyboard.row(ikb("🥝 QIWI", data="user_refill_method:QIWI"))
    if get_payments.way_yoomoney == "True":
        keyboard.row(ikb("🔮 ЮMoney", data="user_refill_method:Yoomoney"))
    if get_payments.way_cryptobot == "True":
        keyboard.row(ikb("💎 CryptoBot", data="user_refill_method:CryptoBot"))

    keyboard.row(ikb("🔙 Вернуться", data="user_profile"))

    return keyboard.as_markup()


# Проверка платежа
def refill_bill_finl(pay_link: str, pay_receipt: Union[str, int], pay_way: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("🌀 Перейти к оплате", url=pay_link)
    ).row(
        ikb("🔄 Проверить оплату", data=f"Pay:{pay_way}:{pay_receipt}")
    )

    return keyboard.as_markup()


################################################################################
################################## ПОКУПКА ЗВЕЗД ################################
# Выбор пакета звезд
def stars_package_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("⭐ 50 звезд", data="stars_package:50"),
        ikb("⭐ 100 звезд", data="stars_package:100")
    ).row(
        ikb("⭐ 250 звезд", data="stars_package:250"),
        ikb("⭐ 500 звезд", data="stars_package:500")
    ).row(
        ikb("⭐ 1000 звезд", data="stars_package:1000"),
        ikb("✏️ Свой вариант", data="stars_package:custom")
    ).row(
        ikb("🔙 Отменить", data="stars_cancel")
    )

    return keyboard.as_markup()


# Выбор получателя звезд
def stars_recipient_finl(amount_stars: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("👤 Себе", data=f"stars_recipient:self:{amount_stars}"),
        ikb("👥 Другу", data=f"stars_recipient:friend:{amount_stars}")
    ).row(
        ikb("🔙 Назад", data="stars_back_to_packages")
    )

    return keyboard.as_markup()


# Подтверждение покупки звезд
def stars_confirm_finl(amount_stars: int, recipient_type: str, recipient_username: str = None, total_amount: float = None) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    # НЕ передаем total_amount в callback - пересчитаем на сервере для безопасности
    if recipient_username:
        data_cryptobot = f"stars_confirm_cryptobot:{amount_stars}:{recipient_type}:{recipient_username}"
        data_balance = f"stars_confirm_balance:{amount_stars}:{recipient_type}:{recipient_username}"
    else:
        data_cryptobot = f"stars_confirm_cryptobot:{amount_stars}:{recipient_type}:none"
        data_balance = f"stars_confirm_balance:{amount_stars}:{recipient_type}:none"

    keyboard.row(
        ikb("💎 Оплатить через CryptoBot", data=data_cryptobot)
    ).row(
        ikb("💰 Оплатить с баланса", data=data_balance)
    ).row(
        ikb("❌ Отменить", data="stars_cancel")
    )

    return keyboard.as_markup()


# Кнопка отмены при вводе суммы пополнения
def refill_cancel_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        ikb("❌ Отменить", data="user_profile")
    )
    
    return keyboard.as_markup()


################################################################################
#################################### ТОВАРЫ ####################################
# Открытие позиции для просмотра
def products_open_finl(position_id, category_id, remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("💰 Купить товар", data=f"buy_item_open:{position_id}:{remover}")
    ).row(
        ikb("🔙 Вернуться", data=f"buy_category_open:{category_id}:{remover}")
    )

    return keyboard.as_markup()


# Подтверждение покупки товара
def products_confirm_finl(position_id, category_id, get_count) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("✅ Подтвердить", data=f"buy_item_confirm:{position_id}:{get_count}"),
        ikb("❌ Отменить", data=f"buy_position_open:{position_id}:0")
    )

    return keyboard.as_markup()


# Возврат к позиции при отмене ввода
def products_return_finl(position_id, category_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("🔙 Вернуться", data=f"buy_position_open:{position_id}:0")
    )

    return keyboard.as_markup()
