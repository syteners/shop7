# - *- coding: utf- 8 - *-
import sqlite3

from tgbot.data.config import PATH_DATABASE
from tgbot.utils.const_functions import get_unix, ded


# Преобразование полученного списка в словарь
def dict_factory(cursor, row) -> dict:
    save_dict = {}

    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]

    return save_dict


# Форматирование запроса без аргументов
def update_format(sql, parameters: dict) -> tuple[str, list]:
    values = ", ".join([
        f"{item} = ?" for item in parameters
    ])
    sql += f" {values}"

    return sql, list(parameters.values())


# Форматирование запроса с аргументами
def update_format_where(sql, parameters: dict) -> tuple[str, list]:
    sql += " WHERE "

    sql += " AND ".join([
        f"{item} = ?" for item in parameters
    ])

    return sql, list(parameters.values())


################################################################################
# Создание всех таблиц для БД
def create_dbx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory

        ############################################################
        # Создание таблицы с хранением - пользователей
        table_columns = len(con.execute("PRAGMA table_info(storage_users)").fetchall())
        
        if table_columns == 10:
            print("DB was found(1/8)")
        elif table_columns == 9:
            print("DB was found(1/8) | Updating for daily bonus...")
            con.execute("ALTER TABLE storage_users ADD COLUMN user_last_bonus INTEGER DEFAULT 0")
            print("DB updated(1/8) | Daily bonus field added")
        elif table_columns == 8:
            print("DB was found(1/8) | Updating for bonus balance and daily bonus...")
            con.execute("ALTER TABLE storage_users ADD COLUMN user_bonus_balance REAL DEFAULT 0")
            con.execute("ALTER TABLE storage_users ADD COLUMN user_last_bonus INTEGER DEFAULT 0")
            print("DB updated(1/8) | Bonus balance and daily bonus fields added")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_users(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        user_login TEXT,
                        user_name TEXT,
                        user_balance REAL,
                        user_bonus_balance REAL,
                        user_refill REAL,
                        user_give REAL,
                        user_unix INTEGER,
                        user_last_bonus INTEGER
                    )
                """)
            )
            print("DB was not found(1/8) | Creating...")

        # Создание таблицы с хранением - настроек
        table_columns = len(con.execute("PRAGMA table_info(storage_settings)").fetchall())
        
        if table_columns == 12:
            print("DB was found(2/8)")
        elif table_columns == 11:
            print("DB was found(2/8) | Updating for Stars Buy Button...")
            con.execute("ALTER TABLE storage_settings ADD COLUMN status_stars_buy TEXT DEFAULT 'False'")
            print("DB updated(2/8) | Stars buy button field added")
        elif table_columns == 10:
            print("DB was found(2/8) | Updating for Stars Markup and Buy Button...")
            con.execute("ALTER TABLE storage_settings ADD COLUMN stars_markup INTEGER DEFAULT 10")
            con.execute("ALTER TABLE storage_settings ADD COLUMN status_stars_buy TEXT DEFAULT 'False'")
            print("DB updated(2/8) | Stars markup and buy button fields added")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_settings(
                        status_work TEXT,
                        status_refill TEXT,
                        status_buy TEXT,
                        status_stars_buy TEXT,
                        misc_faq TEXT,
                        misc_support TEXT,
                        misc_bot TEXT,
                        misc_update TEXT,
                        misc_profit_day INTEGER,
                        misc_profit_week INTEGER,
                        misc_profit_month INTEGER,
                        stars_markup INTEGER
                    )
                """)
            )

            con.execute(
                ded(f"""
                    INSERT INTO storage_settings(
                        status_work,
                        status_refill,
                        status_buy,
                        status_stars_buy,
                        misc_faq,
                        misc_support,
                        misc_bot,
                        misc_update,
                        misc_profit_day,
                        misc_profit_week,
                        misc_profit_month,
                        stars_markup
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """),
                [
                    'True',
                    'False',
                    'False',
                    'False',
                    'None',
                    'None',
                    'None',
                    'False',
                    get_unix(),
                    get_unix(),
                    get_unix(),
                    10,
                ]
            )
            print("DB was not found(2/8) | Creating...")

        ############################################################
        # Создание таблицы с хранением - данных платежных систем
        table_columns = len(con.execute("PRAGMA table_info(storage_payment)").fetchall())
        
        if table_columns == 7:
            print("DB was found(3/8)")
        elif table_columns == 5:
            print("DB was found(3/8) | Updating for CryptoBot...")
            con.execute("ALTER TABLE storage_payment ADD COLUMN cryptobot_token TEXT DEFAULT 'None'")
            con.execute("ALTER TABLE storage_payment ADD COLUMN way_cryptobot TEXT DEFAULT 'False'")
            print("DB updated(3/8) | CryptoBot fields added")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_payment(
                        qiwi_login TEXT,
                        qiwi_token TEXT,
                        yoomoney_token TEXT,
                        way_qiwi TEXT,
                        way_yoomoney TEXT,
                        cryptobot_token TEXT,
                        way_cryptobot TEXT
                    )
                """)
            )

            con.execute(
                ded(f"""
                    INSERT INTO storage_payment(
                        qiwi_login,
                        qiwi_token,
                        yoomoney_token,
                        way_qiwi,
                        way_yoomoney,
                        cryptobot_token,
                        way_cryptobot
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """),
                [
                    'None',
                    'None',
                    'None',
                    'False',
                    'False',
                    'None',
                    'False',
                ]
            )
            print("DB was not found(3/8) | Creating...")

        ############################################################
        # Создание таблицы с хранением - пополнений пользователей
        if len(con.execute("PRAGMA table_info(storage_refill)").fetchall()) == 7:
            print("DB was found(4/8)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_refill(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        refill_comment TEXT,
                        refill_amount REAL,
                        refill_receipt TEXT,
                        refill_method TEXT,
                        refill_unix INTEGER
                    )
                """)
            )
            print("DB was not found(4/8) | Creating...")

        ############################################################
        # Создание таблицы с хранением - категорий
        if len(con.execute("PRAGMA table_info(storage_category)").fetchall()) == 4:
            print("DB was found(5/8)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_category(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_id INTEGER,
                        category_name TEXT,
                        category_unix INTEGER
                    )
                """)
            )
            print("DB was not found(5/8) | Creating...")

        ############################################################
        # Создание таблицы с хранением - позиций
        if len(con.execute("PRAGMA table_info(storage_position)").fetchall()) == 8:
            print("DB was found(6/8)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_position(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_id INTEGER,
                        position_id INTEGER,
                        position_name TEXT,
                        position_price REAL,
                        position_desc TEXT,
                        position_photo TEXT,
                        position_unix INTEGER
                    )
                """)
            )
            print("DB was not found(6/8) | Creating...")

        ############################################################
        # Создание таблицы с хранением - товаров
        if len(con.execute("PRAGMA table_info(storage_item)").fetchall()) == 7:
            print("DB was found(7/8)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_item(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        category_id INTEGER,
                        position_id INTEGER,
                        item_id INTEGER,
                        item_unix INTEGER,
                        item_data TEXT
                    )
                """)
            )
            print("DB was not found(7/8) | Creating...")

        ############################################################
        # Создание таблицы с хранением - покупок
        if len(con.execute("PRAGMA table_info(storage_purchases)").fetchall()) == 14:
            print("DB was found(8/9)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_purchases(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        user_balance_before REAL,
                        user_balance_after REAL,
                        purchase_receipt TEXT,
                        purchase_data TEXT,
                        purchase_count INTEGER,
                        purchase_price REAL,
                        purchase_price_one REAL,
                        purchase_position_id INTEGER,
                        purchase_position_name TEXT,
                        purchase_category_id INTEGER,
                        purchase_category_name TEXT,
                        purchase_unix INTEGER
                    )
                """)
            )
            print("DB was not found(8/9) | Creating...")

        ############################################################
        # Создание таблицы с хранением - покупок звезд Telegram
        if len(con.execute("PRAGMA table_info(storage_stars_purchases)").fetchall()) == 9:
            print("DB was found(9/11)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_stars_purchases(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        recipient_id INTEGER,
                        recipient_username TEXT,
                        amount_stars INTEGER,
                        amount_paid REAL,
                        markup_percent INTEGER,
                        purchase_receipt TEXT,
                        purchase_unix INTEGER
                    )
                """)
            )
            print("DB was not found(9/11) | Creating...")

        ############################################################
        # Создание таблицы с хранением - промокодов
        if len(con.execute("PRAGMA table_info(storage_promocodes)").fetchall()) == 7:
            print("DB was found(10/11)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_promocodes(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        promocode TEXT UNIQUE,
                        balance REAL,
                        usage_count INTEGER,
                        max_usage INTEGER,
                        created_by INTEGER,
                        created_unix INTEGER
                    )
                """)
            )
            print("DB was not found(10/11) | Creating...")

        ############################################################
        # Создание таблицы с хранением - использований промокодов
        if len(con.execute("PRAGMA table_info(storage_promocode_usage)").fetchall()) == 4:
            print("DB was found(11/11)")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE storage_promocode_usage(
                        increment INTEGER PRIMARY KEY AUTOINCREMENT,
                        promocode TEXT,
                        user_id INTEGER,
                        used_unix INTEGER
                    )
                """)
            )
            print("DB was not found(11/11) | Creating...")
