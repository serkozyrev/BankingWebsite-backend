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

def add(transaction_type, description, amount, day, month, year, category, rate, account_type, dollars):
    if transaction_type == 'revenue':
        try:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute('insert into revenue(description, revenuebalance, transactionday,'
                               ' transactionmonth, transactionyear, category, transactiontype) values(%s, %s, %s, %s, %s, %s, %s)',
                               (description, amount, day, month, year, category, transaction_type))
        except:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute('insert into revenue(description, revenuebalance, transactionday,'
                               ' transactionmonth, transactionyear, category, transactiontype) values(%s, %s, %s, %s, %s, %s, %s)',
                               (description, amount, day, month, year, category, transaction_type))

        if category == 'moneyReceiving':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Мой Счет'")
                    account_balance = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance = float(account_balance[0]) + float(amount)

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Мой Счет'", (round(new_balance, 2),))
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
        elif category == 'pensionPapa':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Мой Счет'")
                    account_balance_pension = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_pension = float(account_balance_pension[0]) + float(amount)

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                   (round(new_balance_after_pension, 2),))
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
        elif category == 'pensionDina':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Счет Дины'")
                    account_balance_pension = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_pension = float(account_balance_pension[0]) + float(amount)

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                   (round(new_balance_after_pension, 2),))
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

    elif transaction_type == 'expense':
        try:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute('insert into expense(description, expensebalance, transactionday,'
                               ' transactionmonth, transactionyear, amountindollars, category, transactiontype, account_type) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                               (description, amount, day, month, year,round(dollars, 2), category, transaction_type, account_type))
        except:
            return jsonify({'message': 'Не получилось добавить новую запись, попробуйте позже'})

        if category == 'moneySend':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Мой Счет'")
                    account_balance_send = cursor.fetchone()
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_send = float(account_balance_send[0]) - float(amount)

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Мой Счет'", (round(new_balance_after_send, 2), ))
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Счет Дины'")
                    account_balance_dina = cursor.fetchone()
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_dina_balance = float(account_balance_dina[0]) + float(amount)

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Счет Дины'", (round(new_dina_balance, 2), ))
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
        elif category == 'moneySendSnezhana':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Счет Дины'")
                    account_balance_send = cursor.fetchone()
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_send = float(account_balance_send[0]) - float(amount)

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Счет Дины'", (round(new_balance_after_send, 2), ))
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Счет Снежаны'")
                    account_balance_dina = cursor.fetchone()
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_snezhana_balance = float(account_balance_dina[0]) + float(amount)

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Счет Снежаны'", (round(new_snezhana_balance, 2), ))
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
        elif account_type == 'SnezhanaAccount':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Счет Снежаны'")
                    account_balance_send = cursor.fetchone()
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_expense = float(account_balance_send[0]) - float(amount)

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Счет Снежаны'", (round(new_balance_after_expense, 2), ))
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
        elif account_type == 'PapaAccount':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Мой Счет'")
                    account_balance_send = cursor.fetchone()
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_expense = float(account_balance_send[0]) - float(amount)

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Мой Счет'", (round(new_balance_after_expense, 2), ))
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
        elif account_type == 'DinaAccount':
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select userbalance from account where description='Счет Дины'")
                    account_balance_send = cursor.fetchone()
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_expense = float(account_balance_send[0]) - float(amount)

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Счет Дины'", (round(new_balance_after_expense, 2), ))
            except:
                return jsonify({'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})