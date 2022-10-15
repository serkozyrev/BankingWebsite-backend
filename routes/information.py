from flask import jsonify
import os
from datetime import datetime
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

def collect_information():
    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from revenues order by transactionyear desc, transactionmonth collate numeric_value desc, transactionday desc')
            revenues = cursor.fetchall()
    except:
        return jsonify({'message': 'Не получилось получить данные о расходах, попробуйте позже'})

    revenues_list = []

    for revenue in revenues:

        new_revenue = {
            'id':revenue[0], 'description':revenue[1], 'amount':f'{revenue[2]:,}',
            'day':revenue[3], 'month':revenue[4], 'year':revenue[5]
        }
        revenues_list.append(new_revenue)

    current_month = datetime.now().month
    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from expenses where account_type='PapaAccount'"
                           " or account_type='SnezhanaAccount' order by transactionyear desc, transactionmonth collate numeric_value desc, transactionday desc")
            expenses = cursor.fetchall()
    except:
        return jsonify({'message': 'Не получилось получить данные о доходах, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from expenses where account_type='DinaAccount' order by transactionyear desc, transactionmonth collate numeric_value desc, transactionday desc")
            expenses_dina = cursor.fetchall()
    except:
        return jsonify({'message': 'Не получилось получить данные о доходах, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"select sum(expensebalance) "
                           f"from expense"
                           f" group by transactionmonth,account_type"
                           f" having transactionmonth='%s' and account_type='PapaAccount'", (current_month,))
            expenses_total = cursor.fetchone()
    except:
        return jsonify({'message': 'Не получилось получить данные о расходах за месяц, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"select sum(expensebalance) "
                           f"from expense"
                           f" group by transactionmonth,account_type"
                           f" having transactionmonth='%s' and account_type='DinaAccount'", (current_month,))
            expenses_total_dina = cursor.fetchone()
    except:
        return jsonify({'message': 'Не получилось получить данные о расходах за месяц, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"select sum(expensebalance) "
                           f"from expense"
                           f" group by transactionmonth,account_type"
                           f" having transactionmonth='%s' and account_type='SnezhanaAccount'", (current_month,))
            expenses_total_snezhana = cursor.fetchone()
    except:
        return jsonify({'message': 'Не получилось получить данные о расходах за месяц, попробуйте позже'})
    expenses_list = []
    expenses_list_dina = []

    if expenses_total is None:
        total_expense = 0
    else:
        for total in expenses_total:
            total_expense = total

    if expenses_total_dina is None:
        total_expense_dina = 0
    else:
        for total in expenses_total_dina:
            total_expense_dina = total

    if expenses_total_snezhana is None:
        total_expense_snezhana = 0
    else:
        for total in expenses_total_snezhana:
            total_expense_snezhana = total
    for expense in expenses:

        new_expense = {
            'id': expense[0], 'description': expense[1], 'amount': f'{expense[2]:,}',
            'day': expense[3], 'month': expense[4], 'year': expense[5],
            'amountindollar': f'{expense[6]:,}', 'category': expense[7], 'type': expense[8], 'accountType': expense[9]
        }
        expenses_list.append(new_expense)

    for expense in expenses_dina:

        new_expense_dina = {
            'id': expense[0], 'description': expense[1], 'amount': f'{expense[2]:,}',
            'day': expense[3], 'month': expense[4], 'year': expense[5],
            'amountindollar': f'{expense[6]:,}', 'category': expense[7], 'type': expense[8], 'accountType': expense[9]
        }
        expenses_list_dina.append(new_expense_dina)

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


    dina_balance = float(account_balance_dina[0])
    my_balance = float(account_balance_mine[0])
    snezhana_balance = float(account_balance_snezhana[0])

    return {'message': 'Record Saved Successfully', 'expensesPapa': expenses_list,
                    'expensesDina': expenses_list_dina, 'revenues': revenues_list,
                    'total': f'{round(total_expense, 2):,}', 'totalDina': f'{round(total_expense_dina, 2):,}',
                    'dina_balance': f'{round(dina_balance, 2):,}', 'my_balance': f'{round(my_balance, 2):,}',
                    'snezhana_balance': f'{round(snezhana_balance, 2):,}',
                    'totalSnezhana': f'{round(total_expense_snezhana, 2):,}'}