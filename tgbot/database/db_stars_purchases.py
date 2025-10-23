# - *- coding: utf- 8 - *-
import sqlite3

from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format


# Модель таблицы
class StarsPurchaseModel(BaseModel):
    increment: int
    user_id: int
    recipient_id: int
    recipient_username: str
    amount_stars: int
    amount_paid: float
    markup_percent: int
    purchase_receipt: str
    purchase_unix: int


# Работа с покупками звезд
class StarsPurchasex:
    storage_name = "storage_stars_purchases"

    # Добавление записи
    @staticmethod
    def add(
        user_id: int,
        recipient_id: int,
        recipient_username: str,
        amount_stars: int,
        amount_paid: float,
        markup_percent: int,
        purchase_receipt: str,
        purchase_unix: int
    ):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            con.execute(
                f"INSERT INTO {StarsPurchasex.storage_name} "
                f"(user_id, recipient_id, recipient_username, amount_stars, amount_paid, "
                f"markup_percent, purchase_receipt, purchase_unix) "
                f"VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [user_id, recipient_id, recipient_username, amount_stars, amount_paid,
                 markup_percent, purchase_receipt, purchase_unix]
            )

    # Получение записи
    @staticmethod
    def get(**kwargs) -> StarsPurchaseModel | None:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {StarsPurchasex.storage_name}"

            if kwargs:
                sql += " WHERE "
                sql += " AND ".join([f"{key} = ?" for key in kwargs.keys()])
                parameters = list(kwargs.values())
                response = con.execute(sql, parameters).fetchone()
            else:
                response = con.execute(sql).fetchone()

            if response is not None:
                return StarsPurchaseModel(**response)
            else:
                return None

    # Получение всех записей
    @staticmethod
    def gets(**kwargs) -> list[StarsPurchaseModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {StarsPurchasex.storage_name}"

            if kwargs:
                sql += " WHERE "
                sql += " AND ".join([f"{key} = ?" for key in kwargs.keys()])
                parameters = list(kwargs.values())
                response = con.execute(sql, parameters).fetchall()
            else:
                response = con.execute(sql).fetchall()

            return [StarsPurchaseModel(**item) for item in response]

    # Получение всех записей
    @staticmethod
    def get_all() -> list[StarsPurchaseModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {StarsPurchasex.storage_name}"
            response = con.execute(sql).fetchall()

            return [StarsPurchaseModel(**item) for item in response]

    # Редактирование записи
    @staticmethod
    def update(increment, **kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {StarsPurchasex.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)
            parameters.append(increment)
            sql += " WHERE increment = ?"

            con.execute(sql, parameters)

    # Удаление записи
    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {StarsPurchasex.storage_name}"

            if kwargs:
                sql += " WHERE "
                sql += " AND ".join([f"{key} = ?" for key in kwargs.keys()])
                parameters = list(kwargs.values())
                con.execute(sql, parameters)
            else:
                con.execute(sql)
