# - *- coding: utf- 8 - *-
from aiogram import BaseMiddleware, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from tgbot.data.config import get_required_channels, get_admins


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        bot: Bot = data.get("bot")
        user_id = data.get("event_from_user").id
        
        if user_id in get_admins():
            return await handler(event, data)
        
        required_channels = get_required_channels()
        
        if not required_channels:
            return await handler(event, data)
        
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
                    except Exception as e:
                        pass
            except Exception as e:
                pass
        
        if unsubscribed_channels:
            channel_buttons.append([
                InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subscription")
            ])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=channel_buttons)
            
            if isinstance(event, Message):
                await event.answer(
                    "⚠️ <b>Для использования бота необходимо подписаться на наши каналы!</b>\n\n"
                    "👇 <b>Нажмите на кнопки ниже, чтобы подписаться:</b>\n\n"
                    "После подписки на все каналы нажмите кнопку <b>✅ Проверить подписку</b>",
                    reply_markup=keyboard
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "⚠️ Для использования бота необходимо подписаться на наши каналы!",
                    show_alert=True
                )
            
            return
        
        return await handler(event, data)
