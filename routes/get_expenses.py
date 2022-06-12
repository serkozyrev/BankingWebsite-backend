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

def expenses():
    currentMonth = datetime.now().month
    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from expense where account_type='PapaAccount'"
                           " or account_type='SnezhanaAccount' order by transactionmonth desc,transactionday desc,  transactionyear desc")
            expenses = cursor.fetchall()
    except:
        return jsonify({'message': 'Не получилось получить данные о доходах, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                "select * from expense where account_type='DinaAccount' order by transactionmonth desc,transactionday desc,  transactionyear desc")
            expenses_dina = cursor.fetchall()
    except:
        return jsonify({'message': 'Не получилось получить данные о доходах, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"select sum(expensebalance) "
                           f"from expense"
                           f" group by transactionmonth,account_type"
                           f" having transactionmonth='%s' and account_type='PapaAccount'", (currentMonth,))
            expenses_total = cursor.fetchone()
    except:
        return jsonify({'message': 'Не получилось получить данные о расходах за месяц, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"select sum(expensebalance) "
                           f"from expense"
                           f" group by transactionmonth,account_type"
                           f" having transactionmonth='%s' and account_type='DinaAccount'", (currentMonth,))
            expenses_total_dina = cursor.fetchone()
    except:
        return jsonify({'message': 'Не получилось получить данные о расходах за месяц, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"select sum(expensebalance) "
                           f"from expense"
                           f" group by transactionmonth,account_type"
                           f" having transactionmonth='%s' and account_type='SnezhanaAccount'", (currentMonth,))
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
            'amountindollar': f'{expense[6]:,}', 'category': expense[7], 'type': expense[8]
        }
        expenses_list.append(new_expense)

    for expense in expenses_dina:
        new_expense_dina = {
            'id': expense[0], 'description': expense[1], 'amount': f'{expense[2]:,}',
            'day': expense[3], 'month': expense[4], 'year': expense[5],
            'amountindollar': f'{expense[6]:,}', 'category': expense[7], 'type': expense[8]
        }
        expenses_list_dina.append(new_expense_dina)
    return jsonify({'expensesPapa': expenses_list, 'expensesDina': expenses_list_dina,
                    'total': f'{round(total_expense, 2):,}', 'totalDina': f'{round(total_expense_dina, 2):,}',
                    'totalSnezhana': f'{round(total_expense_snezhana, 2):,}'})