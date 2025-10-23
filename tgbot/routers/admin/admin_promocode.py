# - *- coding: utf- 8 - *-
import string
import random
from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from tgbot.database.db_promocodes import Promocodex
from tgbot.keyboards.inline_promocode import (
    promocode_admin_keyboard,
    promocode_usage_type_keyboard,
    promocode_list_keyboard,
    promocode_info_keyboard
)
from tgbot.keyboards.reply_main import settings_frep
from tgbot.utils.const_functions import get_unix

router = Router(name=__name__)


class PromocodeAdminState(StatesGroup):
    enter_balance = State()
    enter_usage = State()


@router.message(F.text == "🎟️ Промокоды")
async def admin_promocodes_menu(message: Message):
    await message.answer(
        "🎟️ <b>Управление промокодами</b>\n\n"
        "Выберите действие:",
        reply_markup=promocode_admin_keyboard()
    )


@router.callback_query(F.data == "admin_promocodes")
async def admin_promocodes_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎟️ <b>Управление промокодами</b>\n\n"
        "Выберите действие:",
        reply_markup=promocode_admin_keyboard()
    )


@router.callback_query(F.data == "admin_create_promocode")
async def admin_create_promocode(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PromocodeAdminState.enter_balance)
    await callback.message.edit_text(
        "💰 <b>Создание промокода</b>\n\n"
        "Введите сумму бонусного баланса, которую получит пользователь при активации промокода:\n\n"
        "Пример: <code>100</code> или <code>50.5</code>",
        reply_markup=None
    )


@router.message(PromocodeAdminState.enter_balance)
async def promocode_enter_balance(message: Message, state: FSMContext):
    try:
        balance = float(message.text.strip())
        
        if balance <= 0:
            await message.answer(
                "❌ Сумма должна быть больше 0!\n\n"
                "Попробуйте снова:"
            )
            return
        
        await state.update_data(balance=balance)
        await state.set_state(PromocodeAdminState.enter_usage)
        
        await message.answer(
            f"💰 Сумма: <code>{balance}$</code>\n\n"
            f"Выберите количество использований промокода:",
            reply_markup=promocode_usage_type_keyboard()
        )
    except:
        await message.answer(
            "❌ Неверный формат! Введите число.\n\n"
            "Пример: <code>100</code> или <code>50.5</code>"
        )


@router.callback_query(F.data.startswith("promo_usage:"))
async def promocode_set_usage(callback: CallbackQuery, state: FSMContext):
    max_usage = int(callback.data.split(":")[1])
    
    data = await state.get_data()
    balance = data.get("balance")
    
    promo_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    while Promocodex.get(promocode=promo_code):
        promo_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    Promocodex.add(
        promocode=promo_code,
        balance=balance,
        max_usage=max_usage,
        created_by=callback.from_user.id
    )
    
    usage_text = str(max_usage)
    if max_usage == 999999:
        usage_text = "∞"
    
    await callback.message.edit_text(
        f"✅ <b>Промокод успешно создан!</b>\n\n"
        f"🎟️ Промокод: <code>{promo_code}</code>\n"
        f"💰 Сумма: <code>{balance}$</code>\n"
        f"🔄 Использований: {usage_text}\n\n"
        f"Отправьте этот промокод пользователям для активации.",
        reply_markup=promocode_admin_keyboard()
    )
    
    await state.clear()


@router.callback_query(F.data == "admin_list_promocodes")
async def admin_list_promocodes(callback: CallbackQuery):
    promocodes = Promocodex.get_all()
    
    if not promocodes:
        await callback.message.edit_text(
            "📋 <b>Список промокодов пуст</b>\n\n"
            "Создайте первый промокод для начала работы.",
            reply_markup=promocode_admin_keyboard()
        )
        return
    
    promocodes.sort(key=lambda x: x.created_unix, reverse=True)
    
    await callback.message.edit_text(
        f"📋 <b>Список промокодов</b>\n\n"
        f"Всего создано: {len(promocodes)}",
        reply_markup=promocode_list_keyboard(promocodes, 0)
    )


@router.callback_query(F.data.startswith("promo_page:"))
async def promocode_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    promocodes = Promocodex.get_all()
    promocodes.sort(key=lambda x: x.created_unix, reverse=True)
    
    await callback.message.edit_text(
        f"📋 <b>Список промокодов</b>\n\n"
        f"Всего создано: {len(promocodes)}",
        reply_markup=promocode_list_keyboard(promocodes, page)
    )


@router.callback_query(F.data.startswith("promo_info:"))
async def promocode_info(callback: CallbackQuery):
    promo_code = callback.data.split(":")[1]
    promocode = Promocodex.get(promocode=promo_code)
    
    if not promocode:
        await callback.answer("❌ Промокод не найден!", show_alert=True)
        return
    
    usage_text = f"{promocode.usage_count}/{promocode.max_usage}"
    if promocode.max_usage == 999999:
        usage_text = f"{promocode.usage_count}/∞"
    
    await callback.message.edit_text(
        f"🎟️ <b>Информация о промокоде</b>\n\n"
        f"Код: <code>{promocode.promocode}</code>\n"
        f"💰 Сумма: <code>{promocode.balance}$</code>\n"
        f"📊 Использовано: {usage_text}\n"
        f"📅 Создан: {promocode.created_unix}",
        reply_markup=promocode_info_keyboard(promo_code)
    )


@router.callback_query(F.data.startswith("promo_delete:"))
async def promocode_delete(callback: CallbackQuery):
    promo_code = callback.data.split(":")[1]
    
    Promocodex.delete(promocode=promo_code)
    
    await callback.answer("✅ Промокод удален!", show_alert=True)
    await callback.message.edit_text(
        "✅ <b>Промокод успешно удален!</b>",
        reply_markup=promocode_admin_keyboard()
    )
