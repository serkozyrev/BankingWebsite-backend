from flask import jsonify
import os
from dotenv import load_dotenv
from database import Database
from database import CursorFromConnectionFromPool

load_dotenv()
DB_PWD = os.getenv('DB_PWD')
DB_USER = os.getenv('DB_USER')
DB_HOST = os.getenv('DB_HOST')

DB = os.getenv('DB')
Database.initialize(user=f'{DB_USER}',
                    password=f'{DB_PWD}',
                    host=f'{DB_HOST}',
                    port=5432,
                    database=f'{DB}')

def provide_account_info():
    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select userbalance from account where description='Мой Счет'")
            account_balance_mine = cursor.fetchone()
    except:
        return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select userbalance from account where description='Счет Дины'")
            account_balance_dina = cursor.fetchone()
    except:
        return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select userbalance from account where description='Счет Снежаны'")
            account_balance_snezhana = cursor.fetchone()
    except:
        return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

    my_balance_info = f'{round(float(account_balance_mine[0]),2):,}'
    dina_balance_info = f'{round(float(account_balance_dina[0]), 2):,}'
    snezhana_balance_info = f'{round(float(account_balance_snezhana[0]), 2):,}'
    return jsonify({'dina_balance': dina_balance_info, 'my_balance': my_balance_info, 'snezhana_balance': snezhana_balance_info})