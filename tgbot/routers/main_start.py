# - *- coding: utf- 8 - *-
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery

from tgbot.database.db_settings import Settingsx
from tgbot.keyboards.inline_user import user_support_finl
from tgbot.keyboards.reply_main import menu_frep
from tgbot.utils.const_functions import ded
from tgbot.utils.misc.bot_filters import IsBuy, IsRefill, IsWork
from tgbot.utils.misc.bot_models import FSM, ARS

# Игнор-колбэки покупок
prohibit_buy = [
    'buy_category_swipe',
    'buy_category_open',
    'buy_position_swipe',
    'buy_position_open',
    'buy_item_open',
    'buy_item_confirm',
]

# Игнор-колбэки пополнений
prohibit_refill = [
    'user_refill',
    'user_refill_method',
    'Pay:',
    'Pay:QIWI',
    'Pay:Yoomoney',
]

router = Router(name=__name__)


################################################################################
########################### СТАТУС ТЕХНИЧЕСКИХ РАБОТ ###########################
# Фильтр на технические работы - сообщение
@router.message(IsWork())
async def filter_work_message(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    get_settings = Settingsx.get()

    if get_settings.misc_support != "None":
        return await message.answer(
            "<b>⛔ Бот находится на технических работах.</b>",
            reply_markup=user_support_finl(get_settings.misc_support),
        )

    await message.answer("<b>⛔ Бот находится на технических работах.</b>")


# Фильтр на технические работы - колбэк
@router.callback_query(IsWork())
async def filter_work_callback(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await call.answer("⛔ Бот находится на технических работах.", True)


################################################################################
################################# СТАТУС ПОКУПОК ###############################
# Фильтр на доступность покупок - сообщение
@router.message(IsBuy(), F.text == "🎁 Купить")
@router.message(IsBuy(), StateFilter('here_item_count'))
async def filter_buy_message(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer("<b>⛔ Покупки временно отключены.</b>")


# Фильтр на доступность покупок - колбэк
@router.callback_query(IsBuy(), F.text.startswith(prohibit_buy))
async def filter_buy_callback(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await call.answer("⛔ Покупки временно отключены.", True)


################################################################################
############################### СТАТУС ПОПОЛНЕНИЙ ##############################
# Фильтр на доступность пополнения - сообщение
@router.message(IsRefill(), StateFilter('here_pay_amount'))
async def filter_refill_message(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer("<b>⛔ Пополнение временно отключено.</b>")


# Фильтр на доступность пополнения - колбэк
@router.callback_query(IsRefill(), F.text.startswith(prohibit_refill))
async def filter_refill_callback(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await call.answer("⛔ Пополнение временно отключено.", True)


################################################################################
#################################### ПРОЧЕЕ ####################################
# Открытие главного меню
@router.message(F.text.in_(('🔙 Главное меню', '/start')))
async def main_start(message: Message, bot: Bot, state: FSM, arSession: ARS):
    from tgbot.database.db_users import Userx
    
    await state.clear()
    
    get_user = Userx.get(user_id=message.from_user.id)
    user_name = get_user.user_name if get_user else message.from_user.first_name

    await message.answer(
        ded(f"""
            <b>✨ Добро пожаловать, {user_name}! ✨</b>
            
            ━━━━━━━━━━━━━━━━━━━━━
            
            🎉 <b>Рады видеть вас в нашем магазине!</b>
            
            🛍️ <b>Что вы можете сделать:</b>
            
            🎁 <b>Купить</b> — широкий выбор товаров по выгодным ценам
            👤 <b>Профиль</b> — управляйте балансом и смотрите историю покупок
            ⭐ <b>Купить звезды</b> — пополнение звезд Telegram через криптовалюту
            💰 <b>Пополнить баланс</b> — удобные способы пополнения (QIWI, YooMoney, CryptoBot)
            
            📱 <b>Полезное:</b>
            🧮 <b>Наличие товаров</b> — проверьте доступные позиции
            ☎️ <b>Поддержка</b> — свяжитесь с администратором
            ❔ <b>FAQ</b> — ответы на частые вопросы
            
            ━━━━━━━━━━━━━━━━━━━━━
            
            💡 <i>Используйте кнопки меню для навигации</i>
            ⚡ <i>Если кнопки не появились, введите /start</i>
            
            🌟 <b>Приятных покупок!</b> 🌟
        """),
        reply_markup=menu_frep(message.from_user.id),
    )
