# - *- coding: utf- 8 - *-
from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from tgbot.database.db_promocodes import Promocodex
from tgbot.database.db_users import Userx
from tgbot.keyboards.reply_main import menu_frep
from tgbot.utils.const_functions import get_unix

router = Router(name=__name__)


class PromocodeState(StatesGroup):
    enter_code = State()


@router.message(F.text == "🎟️ Промокод")
async def user_promocode_menu(message: Message, state: FSMContext):
    await state.set_state(PromocodeState.enter_code)
    await message.answer(
        "🎟️ <b>Активация промокода</b>\n\n"
        "Введите промокод для получения бонусного баланса.\n\n"
        "💡 <i>Бонусный баланс можно использовать только для покупки товаров в разделе 🛒 Купить.</i>\n\n"
        "Для отмены введите /cancel",
        reply_markup=menu_frep(message.from_user.id)
    )


@router.message(PromocodeState.enter_code, F.text == "/cancel")
async def promocode_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Активация промокода отменена.",
        reply_markup=menu_frep(message.from_user.id)
    )


@router.message(PromocodeState.enter_code)
async def promocode_activate(message: Message, state: FSMContext, bot: Bot):
    from tgbot.data.config import get_admins
    
    promo_code = message.text.strip().upper()
    user_id = message.from_user.id
    
    promocode = Promocodex.get(promocode=promo_code)
    
    if not promocode:
        await message.answer(
            "❌ <b>Промокод не найден!</b>\n\n"
            "Проверьте правильность ввода и попробуйте снова.",
            reply_markup=menu_frep(user_id)
        )
        return
    
    user_usage = Promocodex.get_user_usage(promo_code, user_id)
    if user_usage:
        await message.answer(
            "⚠️ <b>Вы уже использовали этот промокод!</b>\n\n"
            "Каждый промокод можно активировать только один раз.",
            reply_markup=menu_frep(user_id)
        )
        await state.clear()
        return
    
    if promocode.usage_count >= promocode.max_usage:
        await message.answer(
            "⚠️ <b>Промокод исчерпан!</b>\n\n"
            "Все использования данного промокода уже активированы.",
            reply_markup=menu_frep(user_id)
        )
        await state.clear()
        return
    
    get_user = Userx.get(user_id=user_id)
    
    Userx.update(user_id, user_bonus_balance=get_user.user_bonus_balance + promocode.balance)
    
    Promocodex.add_usage(promo_code, user_id)
    Promocodex.update(promo_code, usage_count=promocode.usage_count + 1)
    
    await message.answer(
        f"✅ <b>Промокод успешно активирован!</b>\n\n"
        f"💰 Начислено на бонусный баланс: <code>{promocode.balance}$</code>\n\n"
        f"📊 Ваш текущий бонусный баланс: <code>{get_user.user_bonus_balance + promocode.balance}$</code>\n\n"
        f"💡 <i>Бонусный баланс можно использовать для покупки товаров в разделе 🎁 Купить.</i>",
        reply_markup=menu_frep(user_id)
    )
    
    for admin in get_admins():
        try:
            await bot.send_message(
                admin,
                f"🎟️ <b>Активирован промокод!</b>\n\n"
                f"👤 Пользователь: <a href='tg://user?id={user_id}'>{message.from_user.full_name}</a>\n"
                f"🎟️ Промокод: <code>{promo_code}</code>\n"
                f"💰 Сумма: <code>{promocode.balance}$</code>\n"
                f"📊 Использовано: {promocode.usage_count + 1}/{promocode.max_usage}"
            )
        except:
            pass
    
    await state.clear()


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    await callback.answer("✅ Проверка подписки...", show_alert=False)
    await callback.message.delete()
