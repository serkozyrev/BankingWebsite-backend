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

def delete(transaction_id, transaction_type):
    if transaction_type == 'revenue':
        try:
            with CursorFromConnectionFromPool() as cursors:
                cursors.execute("select * from revenue where revenueid=%s", (transaction_id, ))
                record = cursors.fetchone()
        except:
            return jsonify({'message': 'Не получилось получить данные о записи, попробуйте позже'})

        if record:
            try:
                with CursorFromConnectionFromPool() as cursors:
                    cursors.execute("delete from revenue where revenueid=%s", (transaction_id,))
            except:
                return jsonify({'message': 'Не получилось получить данные о записи, попробуйте позже'})
        if record[6] == 'pensionPapa':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Мой Счет'")
                    account_balance_pension = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_pension = float(account_balance_pension[0]) - float(record[2])

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                   (round(new_balance_after_pension, 2),))
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
        elif record[6] == 'pensionDina':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Счет Дины'")
                    account_balance_pension = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_pension = float(account_balance_pension[0]) - float(record[2])

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                   (round(new_balance_after_pension, 2),))
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

    elif transaction_type == 'expense':
        try:
            with CursorFromConnectionFromPool() as cursors:
                cursors.execute("select * from expense where expenseid=%s", (transaction_id,))
                record = cursors.fetchone()
        except:
            return jsonify({'message': 'Не получилось получить данные о записи, попробуйте позже'})

        if record:
            try:
                with CursorFromConnectionFromPool() as cursors:
                    cursors.execute("delete from expense where expenseid=%s", (transaction_id,))
            except:
                return jsonify({'message': 'Не получилось получить данные о записи, попробуйте позже'})

        if record[7] == 'moneySend':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Мой Счет'")
                    account_balance_send = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_send = float(account_balance_send[0]) + float(record[2])

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                   (round(new_balance_after_send, 2),))
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Счет Дины'")
                    account_balance_dina = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_dina_balance = float(account_balance_dina[0]) - float(record[2])

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                   (round(new_dina_balance, 2),))
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
        elif record[7] == 'moneySendSnezhana':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Счет Дины'")
                    account_balance_send = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_send = float(account_balance_send[0]) + float(record[2])

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                   (round(new_balance_after_send, 2),))
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Счет Снежаны'")
                    account_balance_dina = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_dina_balance = float(account_balance_dina[0]) - float(record[2])

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Счет Снежаны'",
                                   (round(new_dina_balance, 2),))
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
        elif record[9] == 'PapaAccount':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Мой Счет'")
                    account_balance_send = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_expense = float(account_balance_send[0]) + float(record[2])

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                   (round(new_balance_after_expense, 2),))
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
        elif record[9] == 'SnezhanaAccount':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Счет Снежаны'")
                    account_balance_send = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_expense = float(account_balance_send[0]) + float(record[2])

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Счет Снежаны'",
                                   (round(new_balance_after_expense, 2),))
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
        elif record[9] == 'DinaAccount':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Счет Дины'")
                    account_balance_send = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_expense = float(account_balance_send[0]) + float(record[2])

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                   (round(new_balance_after_expense, 2),))
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})