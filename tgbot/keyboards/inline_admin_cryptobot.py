# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.utils.const_functions import ikb


def payment_cryptobot_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("💎 Баланс 💰", data="payment_cryptobot_balance"),
    ).row(
        ikb("💎 Проверить ♻️", data="payment_cryptobot_check"),
    ).row(
        ikb("💎 Изменить 🖍", data="payment_cryptobot_edit"),
    )

    return keyboard.as_markup()
