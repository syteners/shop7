# - *- coding: utf- 8 - *-
import sqlite3

from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format_where, update_format
from tgbot.utils.const_functions import get_unix, ded


class PromocodeModel(BaseModel):
    increment: int
    promocode: str
    balance: float
    usage_count: int
    max_usage: int
    created_by: int
    created_unix: int


class PromocodeUsageModel(BaseModel):
    increment: int
    promocode: str
    user_id: int
    used_unix: int


class Promocodex:
    storage_name = "storage_promocodes"
    usage_storage_name = "storage_promocode_usage"

    @staticmethod
    def add(
            promocode: str,
            balance: float,
            max_usage: int,
            created_by: int,
    ):
        usage_count = 0
        created_unix = get_unix()

        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory

            con.execute(
                ded(f"""
                    INSERT INTO {Promocodex.storage_name} (
                        promocode,
                        balance,
                        usage_count,
                        max_usage,
                        created_by,
                        created_unix
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """),
                [
                    promocode,
                    balance,
                    usage_count,
                    max_usage,
                    created_by,
                    created_unix,
                ],
            )

    @staticmethod
    def get(**kwargs) -> PromocodeModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Promocodex.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchone()

            if response is not None:
                response = PromocodeModel(**response)

            return response

    @staticmethod
    def gets(**kwargs) -> list[PromocodeModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Promocodex.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchall()

            if len(response) >= 1:
                response = [PromocodeModel(**cache_object) for cache_object in response]

            return response

    @staticmethod
    def get_all() -> list[PromocodeModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Promocodex.storage_name}"

            response = con.execute(sql).fetchall()

            if len(response) >= 1:
                response = [PromocodeModel(**cache_object) for cache_object in response]

            return response

    @staticmethod
    def update(promocode: str, **kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Promocodex.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)
            parameters.append(promocode)

            con.execute(sql + " WHERE promocode = ?", parameters)

    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Promocodex.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            con.execute(sql, parameters)

    @staticmethod
    def add_usage(promocode: str, user_id: int):
        used_unix = get_unix()

        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory

            con.execute(
                ded(f"""
                    INSERT INTO {Promocodex.usage_storage_name} (
                        promocode,
                        user_id,
                        used_unix
                    ) VALUES (?, ?, ?)
                """),
                [
                    promocode,
                    user_id,
                    used_unix,
                ],
            )

    @staticmethod
    def get_user_usage(promocode: str, user_id: int) -> PromocodeUsageModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Promocodex.usage_storage_name} WHERE promocode = ? AND user_id = ?"

            response = con.execute(sql, [promocode, user_id]).fetchone()

            if response is not None:
                response = PromocodeUsageModel(**response)

            return response

    @staticmethod
    def get_usage_count(promocode: str) -> int:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT COUNT(*) as count FROM {Promocodex.usage_storage_name} WHERE promocode = ?"

            response = con.execute(sql, [promocode]).fetchone()

            if response is not None:
                return response['count']

            return 0
