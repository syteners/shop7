# - *- coding: utf- 8 - *-
import json
from typing import Union

from aiogram import Bot
from aiogram.types import Message, CallbackQuery

from tgbot.database.db_payments import Paymentsx
from tgbot.utils.const_functions import ded, send_errors, gen_id
from tgbot.utils.misc.bot_models import ARS
from tgbot.utils.misc_functions import send_admins


class CryptoBotAPI:
    def __init__(
            self,
            bot: Bot,
            arSession: ARS,
            update: Union[Message, CallbackQuery] = None,
            token: str = None,
            skipping_error: bool = False,
    ):
        if token is not None:
            self.token = token
        else:
            get_payment = Paymentsx.get()
            self.token = get_payment.cryptobot_token

        self.base_url = 'https://pay.crypt.bot/api/'
        self.headers = {
            'Crypto-Pay-API-Token': self.token,
        }

        self.bot = bot
        self.arSession = arSession
        self.update = update
        self.skipping_error = skipping_error

    async def error_wallet_admin(self, error_code: str = "Unknown"):
        if not self.skipping_error:
            await send_admins(
                self.bot,
                f"<b>💎 CryptoBot недоступен. Как можно быстрее его замените</b>\n"
                f"❗️ Error: <code>{error_code}</code>"
            )

    async def error_wallet_user(self):
        if self.update is not None and not self.skipping_error:
            if isinstance(self.update, Message):
                await self.update.edit_text(
                    "<b>❗ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                    "⌛ Попробуйте чуть позже.</b>"
                )
            elif isinstance(self.update, CallbackQuery):
                await self.update.answer(
                    "❗ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                    "⌛ Попробуйте чуть позже."
                )
            else:
                await send_errors(self.bot, 4938222)

    async def check(self) -> tuple[bool, str]:
        status, response = await self._request("getMe")

        if status:
            app_name = response.get('name', 'Unknown')
            payment_processing_bot = response.get('payment_processing_bot_username', 'Unknown')

            return True, ded(f"""
                <b>💎 CryptoBot кошелёк полностью функционирует ✅</b>
                ➖➖➖➖➖➖➖➖➖➖
                ▪️ Приложение: <code>{app_name}</code>
                ▪️ Платёжный бот: <code>@{payment_processing_bot}</code>
                ▪️ Токен: <code>{self.token[:10]}...{self.token[-10:]}</code>
            """)
        else:
            return False, ded(f"""
                <b>💎 CryptoBot данные не прошли проверку ❌</b>
                ▶️ Код ошибки: <code>{response}</code>
            """)

    async def balance(self) -> str:
        status, response = await self._request("getBalance")

        if status:
            balances = []
            for balance in response:
                currency_code = balance.get('currency_code', 'Unknown')
                available = balance.get('available', '0')
                balances.append(f"▪️ {currency_code}: <code>{available}</code>")

            balance_text = "\n".join(balances) if balances else "Нет доступных балансов"

            return ded(f"""
                <b>💎 Баланс кошелька CryptoBot</b>
                ➖➖➖➖➖➖➖➖➖➖
                {balance_text}
            """)
        else:
            return ded(f"""
                <b>💎 Не удалось получить баланс CryptoBot кошелька ❌</b>
                ❗️ Error: <code>{response}</code>
            """)

    async def edit(self) -> tuple[bool, str]:
        status, response = await self.check()

        if status:
            return True, ded(f"""
                <b>💎 CryptoBot кошелёк был успешно изменён ✅</b>
            """)
        else:
            return False, ""

    async def bill(self, pay_amount: float, stars_markup: int = 0) -> tuple[str, str, int]:
        bill_receipt = gen_id()

        amount_with_markup = pay_amount
        if stars_markup > 0:
            amount_with_markup = round(pay_amount * (1 + stars_markup / 100), 2)

        data = {
            'amount': str(amount_with_markup),
            'currency_type': 'fiat',
            'fiat': 'USD',
            'description': f'Пополнение баланса #{bill_receipt}',
            'paid_btn_name': 'callback',
            'paid_btn_url': f'https://t.me/your_bot',
        }

        status, response = await self._request("createInvoice", data, http_method="POST")

        if status:
            bill_url = response.get('pay_url', '')
            invoice_id = response.get('invoice_id', bill_receipt)

            if stars_markup > 0:
                markup_amount = round(amount_with_markup - pay_amount, 2)
                bill_message = ded(f"""
                    <b>⭐ Покупка звезд Telegram</b>
                    ➖➖➖➖➖➖➖➖➖➖
                    ▪️ Для покупки звезд, нажмите на кнопку ниже 
                    <code>Перейти к оплате</code> и оплатите счёт
                    ▪️ Сумма звезд на баланс: <code>${pay_amount}</code>
                    ▪️ Наценка ({stars_markup}%): <code>+${markup_amount}</code>
                    ▪️ К оплате: <code>${amount_with_markup}</code>
                    ▪️ Платёж через CryptoBot (криптовалюта)
                    ➖➖➖➖➖➖➖➖➖➖
                    ❗️ После оплаты, нажмите на <code>Проверить оплату</code>
                """)
            else:
                bill_message = ded(f"""
                    <b>💰 Пополнение баланса</b>
                    ➖➖➖➖➖➖➖➖➖➖
                    ▪️ Для пополнения баланса, нажмите на кнопку ниже 
                    <code>Перейти к оплате</code> и оплатите выставленный вам счёт
                    ▪️ Сумма пополнения: <code>${pay_amount}</code>
                    ▪️ Платёж через CryptoBot (криптовалюта)
                    ➖➖➖➖➖➖➖➖➖➖
                    ❗️ После оплаты, нажмите на <code>Проверить оплату</code>
                """)

            return bill_message, bill_url, invoice_id
        else:
            await self.error_wallet_user()
            await self.error_wallet_admin(str(response))
            return "", "", 0

    async def bill_check(self, receipt: Union[str, int]) -> tuple[int, float]:
        data = {
            'invoice_ids': str(receipt),
        }

        status, response = await self._request("getInvoices", data, http_method="POST")

        pay_status = 1
        pay_amount = 0

        if status:
            pay_status = 2

            if 'items' in response and len(response['items']) > 0:
                invoice = response['items'][0]
                invoice_status = invoice.get('status', '')

                if invoice_status == 'paid':
                    paid_amount = float(invoice.get('paid_amount', 0))
                    asset = invoice.get('paid_asset', 'USD')
                    
                    if asset == 'USD' or invoice.get('paid_fiat_rate'):
                        pay_amount = paid_amount
                        pay_status = 0
                    else:
                        pay_status = 3
                elif invoice_status == 'active':
                    pay_status = 2
                else:
                    pay_status = 2

        return pay_status, pay_amount

    async def _request(
            self,
            method: str,
            data: dict = None,
            http_method: str = "GET",
    ) -> tuple[bool, any]:
        session = await self.arSession.get_session()

        url = self.base_url + method

        try:
            if http_method == "POST":
                response = await session.post(url, headers=self.headers, json=data)
            else:
                response = await session.get(url, headers=self.headers, params=data)

            response_data = json.loads((await response.read()).decode())

            if response.status == 200 and response_data.get('ok'):
                return True, response_data.get('result', {})
            else:
                error_message = response_data.get('error', {}).get('name', 'Unknown error')
                await self.error_wallet_user()
                await self.error_wallet_admin(f"{response.status} - {error_message}")

                return False, error_message
        except Exception as ex:
            await self.error_wallet_user()
            await self.error_wallet_admin(str(ex))

            return False, str(ex)
