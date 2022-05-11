from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from datetime import datetime
from database import Database
from database import CursorFromConnectionFromPool
from flask_cors import CORS, cross_origin

load_dotenv()
DB_PWD = os.getenv('DB_PWD')
DB_USER = os.getenv('DB_USER')
DB_HOST = os.getenv('DB_HOST')

DB = os.getenv('DB')
app = Flask(__name__)
CORS(app)
Database.initialize(user=f'{DB_USER}',
                    password=f'{DB_PWD}',
                    host=f'{DB_HOST}',
                    port=5432,
                    database=f'{DB}')


def collect_information():
    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from revenues order by transactionmonth desc, transactionyear desc')
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
                           " or account_type='SnezhanaAccount' order by transactionmonth desc, transactionyear desc")
            expenses = cursor.fetchall()
    except:
        return jsonify({'message': 'Не получилось получить данные о доходах, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from expenses where account_type='DinaAccount' order by transactionmonth desc, transactionyear desc")
            expenses_dina = cursor.fetchall()
    except:
        return jsonify({'message': 'Не получилось получить данные о доходах, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"select sum(expensebalance) "
                           f"from expenses"
                           f" group by transactionmonth,account_type"
                           f" having transactionmonth='%s' and account_type='PapaAccount'", (current_month,))
            expenses_total = cursor.fetchone()
    except:
        return jsonify({'message': 'Не получилось получить данные о расходах за месяц, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"select sum(expensebalance) "
                           f"from expenses"
                           f" group by transactionmonth,account_type"
                           f" having transactionmonth='%s' and account_type='DinaAccount'", (current_month,))
            expenses_total_dina = cursor.fetchone()
    except:
        return jsonify({'message': 'Не получилось получить данные о расходах за месяц, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"select sum(expensebalance) "
                           f"from expenses"
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

    return {'message': 'Запись успешно добавлена', 'expensesPapa': expenses_list,
                    'expensesDina': expenses_list_dina, 'revenues': revenues_list,
                    'total': f'{round(total_expense, 2):,}', 'totalDina': f'{round(total_expense_dina, 2):,}',
                    'dina_balance': f'{round(dina_balance, 2):,}', 'my_balance': f'{round(my_balance, 2):,}',
                    'snezhana_balance': f'{round(snezhana_balance, 2):,}',
                    'totalSnezhana': f'{round(total_expense_snezhana, 2):,}'}

@app.route('/api/expenses', methods=['GET'])
@cross_origin()
def get_all_expenses():
    currentMonth = datetime.now().month
    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from expenses where account_type='PapaAccount'"
                           " or account_type='SnezhanaAccount' order by transactionmonth desc, transactionyear desc")
            expenses = cursor.fetchall()
    except:
        return jsonify({'message': 'Не получилось получить данные о доходах, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from expenses where account_type='DinaAccount' order by transactionmonth desc, transactionyear desc")
            expenses_dina = cursor.fetchall()
    except:
        return jsonify({'message': 'Не получилось получить данные о доходах, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"select sum(expensebalance) "
                           f"from expenses"
                           f" group by transactionmonth,account_type"
                           f" having transactionmonth='%s' and account_type='PapaAccount'", (currentMonth, ))
            expenses_total = cursor.fetchone()
    except:
        return jsonify({'message': 'Не получилось получить данные о расходах за месяц, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"select sum(expensebalance) "
                           f"from expenses"
                           f" group by transactionmonth,account_type"
                           f" having transactionmonth='%s' and account_type='DinaAccount'", (currentMonth, ))
            expenses_total_dina = cursor.fetchone()
    except:
        return jsonify({'message': 'Не получилось получить данные о расходах за месяц, попробуйте позже'})

    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"select sum(expensebalance) "
                           f"from expenses"
                           f" group by transactionmonth,account_type"
                           f" having transactionmonth='%s' and account_type='SnezhanaAccount'", (currentMonth, ))
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
            'id':expense[0], 'description':expense[1], 'amount': f'{expense[2]:,}',
            'day':expense[3], 'month':expense[4], 'year':expense[5],
            'amountindollar':f'{expense[6]:,}', 'category':expense[7], 'type':expense[8]
        }
        expenses_list.append(new_expense)

    for expense in expenses_dina:
        new_expense_dina = {
            'id':expense[0], 'description':expense[1], 'amount': f'{expense[2]:,}',
            'day':expense[3], 'month':expense[4], 'year':expense[5],
            'amountindollar':f'{expense[6]:,}', 'category':expense[7], 'type':expense[8]
        }
        expenses_list_dina.append(new_expense_dina)
    return jsonify({'expensesPapa': expenses_list, 'expensesDina':expenses_list_dina,
                    'total': f'{round(total_expense,2):,}', 'totalDina': f'{round(total_expense_dina,2):,}',
                    'totalSnezhana':f'{round(total_expense_snezhana,2):,}'})


@app.route('/api/revenues', methods=['GET'])
@cross_origin()
def get_all_revenue():
    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from revenues order by transactionmonth desc, transactionyear desc')
            revenues = cursor.fetchall()
    except:
        return jsonify({'message': 'Не получилось получить данные о доходах, попробуйте позже'})

    revenues_list = []

    for revenue in revenues:
        new_revenue = {
            'id':revenue[0], 'description':revenue[1], 'amount':f'{revenue[2]:,}',
            'day':revenue[3], 'month':revenue[4], 'year':revenue[5], 'type':revenue[7]
        }
        revenues_list.append(new_revenue)
    return jsonify({'revenues': revenues_list})


@app.route('/api/newrecord', methods=['POST'])
@cross_origin()
def add_new_record():
    transaction_type = request.json['type']
    description = request.json["description"]
    amount = request.json["amount"]
    date = request.json["date"]
    category = request.json["category"]
    rate = request.json["rate"]
    account_type = request.json["accounttype"]

    date_splited = date.split('-')
    day=date_splited[2]
    month=date_splited[1][-1:]
    year=date_splited[0]
    dollars = float(rate)*float(amount)
    "выбрать новые листы дохода и расхода и вернуть вместе с сообщением"

    if transaction_type == 'revenue':
        try:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute('insert into revenues(description, revenuebalance, transactionday,'
                               ' transactionmonth, transactionyear, category, transactiontype) values(%s, %s, %s, %s, %s, %s, %s)',
                               (description, amount, day, month, year, category, transaction_type))
        except:
            return jsonify({'message': 'Не получилось добавить новую запись, попробуйте позже'})

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
                cursor.execute('insert into expenses(description, expensebalance, transactionday,'
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
                    cursor.execute(f"update account set userbalance =%s where description='Мой Счет'", (round(new_balance_after_send, 2), ))
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


    info=collect_information()
    return info


@app.route('/api/copyrecord', methods=['POST'])
@cross_origin()
def copy_record():
    transaction_id = request.json["id"]
    transaction_type = request.json["type"]
    date=datetime.today().strftime('%Y-%m-%d')

    date_splited = date.split('-')
    copy_day = date_splited[2]
    copy_month = date_splited[1][-1:]
    copy_year = date_splited[0]
    if transaction_type == 'expense':
        try:
            with CursorFromConnectionFromPool() as cursors:
                cursors.execute("select * from expenses where expenseid=%s", (transaction_id, ))
                record = cursors.fetchone()
        except:
            with CursorFromConnectionFromPool() as cursors:
                cursors.execute("select * from expenses where expenseid=%s", (transaction_id, ))
                record_backup = cursors.fetchone()
            # return jsonify(
            #     {'message': 'Не получилось получить данные о записи, попробуйте позже'})
        if record is None:
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute('insert into expenses(description, expensebalance, transactionday,'
                                   ' transactionmonth, transactionyear, amountindollars, category, transactiontype,account_type) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                                   (record_backup[1], record_backup[2], copy_day, copy_month, copy_year, round(record_backup[6], 2), record_backup[7],
                                    record_backup[8], record_backup[9]))
            except:
                return jsonify({'message': 'Не получилось добавить новую запись, попробуйте позже'})

            if record_backup[7] == 'moneySend':
                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description='Мой Счет'")
                        account_balance_send = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                new_balance_after_send = float(account_balance_send[0]) - float(record_backup[2])

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

                new_dina_balance = float(account_balance_dina[0]) + float(record_backup[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                       (round(new_dina_balance, 2),))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
            elif record_backup[7] == 'moneySendSnezhana':
                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description='Счет Дины'")
                        account_balance_send = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                new_balance_after_send = float(account_balance_send[0]) - float(record_backup[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
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

                new_snezhana_balance = float(account_balance_dina[0]) + float(record_backup[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Счет Снежаны'",
                                       (round(new_snezhana_balance, 2),))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
            elif record_backup[9] == 'PapaAccount':
                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description='Мой Счет'")
                        account_balance_send = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                new_balance_after_expense = float(account_balance_send[0]) - float(record_backup[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                       (round(new_balance_after_expense, 2),))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
            elif record_backup[9] == 'DinaAccount':
                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description='Счет Дины'")
                        account_balance_send = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                new_balance_after_expense = float(account_balance_send[0]) - float(record_backup[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                       (round(new_balance_after_expense, 2),))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
            elif record_backup[9] == 'SnezhanaAccount':
                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description='Счет Снежаны'")
                        account_balance_send = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                new_balance_after_expense = float(account_balance_send[0]) - float(record_backup[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Счет Снежаны'",
                                       (round(new_balance_after_expense, 2),))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

        else:
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute('insert into expenses(description, expensebalance, transactionday,'
                                   ' transactionmonth, transactionyear, amountindollars, category, transactiontype, account_type) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                                   (record[1], record[2], copy_day, copy_month, copy_year, round(record[6], 2), record[7],
                                    record[8], record[9]))
            except:
                return jsonify({'message': 'Не получилось добавить новую запись, попробуйте позже'})

            if record[7] == 'moneySend':
                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description='Мой Счет'")
                        account_balance_send = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                new_balance_after_send = float(account_balance_send[0]) - float(record[2])

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

                new_dina_balance = float(account_balance_dina[0]) + float(record_backup[2])

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

                new_balance_after_send = float(account_balance_send[0]) - float(record[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
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

                new_snezhana_balance = float(account_balance_dina[0]) + float(record[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Счет Снежаны'",
                                       (round(new_snezhana_balance, 2),))
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

                new_balance_after_expense = float(account_balance_send[0]) - float(record[2])

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

                new_balance_after_expense = float(account_balance_send[0]) - float(record[2])

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

                new_balance_after_expense = float(account_balance_send[0]) - float(record[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                       (round(new_balance_after_expense, 2),))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

    elif transaction_type == 'revenue':
        try:
            with CursorFromConnectionFromPool() as cursors:
                cursors.execute("select * from revenues where revenueid=%s", (transaction_id, ))
                record = cursors.fetchone()
        except:
            with CursorFromConnectionFromPool() as cursors:
                cursors.execute("select * from revenues where revenueid=%s", (transaction_id, ))
                record_backup = cursors.fetchone()
        if record is None:
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute('insert into revenues(description, revenuebalance, transactionday,'
                                   ' transactionmonth, transactionyear, category, transactiontype) values(%s, %s, %s, %s, %s, %s, %s)',
                                   (record_backup[1], record_backup[2], copy_day, copy_month, copy_year, record_backup[6], record_backup[7]))
            except:
                return jsonify({'message': 'Не получилось добавить новую запись, попробуйте позже'})

            if record_backup[6] == 'moneyReceiving':
                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description='Мой Счет'")
                        account_balance = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                new_balance = float(account_balance[0]) + float(record_backup[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                       (round(new_balance, 2),))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
            elif record_backup[6] == 'pensionPapa':
                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description='Мой Счет'")
                        account_balance_pension = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                new_balance_after_pension = float(account_balance_pension[0]) + float(record_backup[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                       (round(new_balance_after_pension, 2),))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
            elif record_backup[6] == 'pensionDina':
                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description='Счет Дины'")
                        account_balance_pension = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                new_balance_after_pension = float(account_balance_pension[0]) + float(record_backup[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                       (round(new_balance_after_pension, 2),))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
        else:
            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute('insert into revenues(description, revenuebalance, transactionday,'
                                   ' transactionmonth, transactionyear, category, transactiontype) values(%s, %s, %s, %s, %s, %s, %s)',
                                   (record[1], record[2], copy_day, copy_month, copy_year, record[6],
                                    record[7]))
            except:
                return jsonify({'message': 'Не получилось добавить новую запись, попробуйте позже'})

            if record[6] == 'moneyReceiving':
                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description='Мой Счет'")
                        account_balance = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                new_balance = float(account_balance[0]) + float(record[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                       (round(new_balance, 2),))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
            elif record[6] == 'pensionPapa':
                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description='Мой Счет'")
                        account_balance_pension = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                new_balance_after_pension = float(account_balance_pension[0]) + float(record[2])

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

                new_balance_after_pension = float(account_balance_pension[0]) + float(record[2])

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                       (round(new_balance_after_pension, 2),))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

    info = collect_information()
    return info


@app.route('/api/deleterecord', methods=['POST'])
@cross_origin()
def delete_record():
    transaction_id = request.json["id"]
    transaction_type = request.json["type"]

    if transaction_type == 'revenue':
        try:
            with CursorFromConnectionFromPool() as cursors:
                cursors.execute("select * from revenues where revenueid=%s", (transaction_id, ))
                record = cursors.fetchone()
        except:
            return jsonify({'message': 'Не получилось получить данные о записи, попробуйте позже'})

        if record:
            try:
                with CursorFromConnectionFromPool() as cursors:
                    cursors.execute("delete from revenues where revenueid=%s", (transaction_id,))
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
                cursors.execute("select * from expenses where expenseid=%s", (transaction_id,))
                record = cursors.fetchone()
        except:
            return jsonify({'message': 'Не получилось получить данные о записи, попробуйте позже'})

        if record:
            try:
                with CursorFromConnectionFromPool() as cursors:
                    cursors.execute("delete from expenses where expenseid=%s", (transaction_id,))
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
                    cursor.execute("select userbalance from account where description='Мой Снежаны'")
                    account_balance_send = cursor.fetchone()
            except:
                return jsonify(
                    {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            new_balance_after_expense = float(account_balance_send[0]) + float(record[2])

            try:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute(f"update account set userbalance =%s where description='Мой Снежаны'",
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

    info = collect_information()
    return info


@app.route('/api/account', methods=['GET'])
@cross_origin()
def get_account_info():
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


@app.route('/api/get_by_id', methods=['POST'])
@cross_origin()
def get_by_id():
    transid = request.json['id']
    transtype = request.json['type']
    if transtype == 'expense':
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from expenses where expenseid=%s', (transid,))
            transaction_by_id = cursor.fetchone()

        expense_transaction_info = {
            'id': transaction_by_id[0], 'description': transaction_by_id[1], 'amount': transaction_by_id[2],
            'day': transaction_by_id[3], 'month': transaction_by_id[4], 'year': transaction_by_id[5],
            'amountindollars': transaction_by_id[6], 'category': transaction_by_id[7], 'type': transtype
        }
        return jsonify({'expense': expense_transaction_info})
    elif transtype == 'revenue':
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from revenues where revenueid = %s', (transid,))
            revenue_transaction_by_id = cursor.fetchone()

        revenue_transaction_info = {
            'id': revenue_transaction_by_id[0], 'description': revenue_transaction_by_id[1],
            'amount': revenue_transaction_by_id[2],
            'day': revenue_transaction_by_id[3], 'month': revenue_transaction_by_id[4],
            'year': revenue_transaction_by_id[5], 'category': revenue_transaction_by_id[6], 'type': transtype
        }
        return jsonify({'revenue': revenue_transaction_info})


@app.route('/api/editrecord', methods=['PATCH'])
@cross_origin()
def edit_record():
    transid = request.json['id']
    transtype=request.json['type']
    description = request.json["description"]
    amount = request.json["amount"]
    date = request.json["date"]
    category = request.json["category"]
    rate = request.json["rate"]


    date_splited = date.split('-')
    day = date_splited[2]
    month = date_splited[1][-1:]
    year = date_splited[0]
    if transtype == 'expense':
        dollars = float(rate) * float(amount)
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from expenses where expenseid = %s', (transid,))
            transaction_by_id = cursor.fetchone()
        if transaction_by_id:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute('update expenses set description=%s, expensebalance=%s, transactionday=%s, '
                               'transactionmonth=%s, transactionyear=%s,amountindollars=%s, category=%s where expenseid=%s',
                               (description, amount, day, month, year, round(dollars, 2), category, transid))
            if transaction_by_id[7] == 'moneySend':
                if float(amount) < transaction_by_id[2]:
                    amount_difference = transaction_by_id[2] - float(amount)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Мой Счет'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) + round(float(amount_difference),2)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Счет Дины'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) - round(float(amount_difference),2)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
                else:
                    amount_difference = float(amount) - transaction_by_id[2]

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Мой Счет'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) - round(float(amount_difference),2)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Счет Дины'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) + round(float(amount_difference),2)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
            elif transaction_by_id[7] == 'moneySendSnezhana':
                if float(amount) < transaction_by_id[2]:
                    amount_difference = transaction_by_id[2] - float(amount)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Мой Дины'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) + round(float(amount_difference),2)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Мой Дины'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Счет Снежаны'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) - round(float(amount_difference),2)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Счет Снежаны'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
                else:
                    amount_difference = float(amount) - transaction_by_id[2]

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Мой Дины'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) - round(float(amount_difference),2)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Мой Дины'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Счет Снежаны'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) + round(float(amount_difference),2)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Счет Снежаны'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            elif float(amount) < transaction_by_id[2]:
                amount_difference = transaction_by_id[2] - float(amount)

                if transaction_by_id[9] == 'PapaAccount':
                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Мой Счет'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) + float(amount_difference)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
                elif transaction_by_id[9] == 'DinaAccount':
                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Счет Дины'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) + float(amount_difference)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
                elif transaction_by_id[9] == 'SnezhanaAccount':
                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Счет Снежаны'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) + float(amount_difference)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Счет Снежаны'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
            else:
                amount_difference=float(amount)-transaction_by_id[2]

                if transaction_by_id[9] == 'PapaAccount':
                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Мой Счет'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) - float(amount_difference)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
                elif transaction_by_id[9] == 'SnezhanaAccount':
                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Счет Снежаны'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) - float(amount_difference)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Счет Снежаны'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
                elif transaction_by_id[9] == 'DinaAccount':
                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Счет Дины'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) - float(amount_difference)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

    elif transtype == 'revenue':
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from revenues where revenueid = %s', (transid,))
            transaction_by_id = cursor.fetchone()
        if transaction_by_id:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute('update revenues set description=%s, revenuebalance=%s, transactionday=%s, '
                               'transactionmonth=%s, transactionyear=%s, category=%s where revenueid=%s',
                               (description, amount, day, month, year, category, transid))

            if float(amount) < transaction_by_id[2]:
                amount_difference = transaction_by_id[2] - float(amount)

                if transaction_by_id[6] == 'pensionPapa':
                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Мой Счет'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) - float(amount_difference)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
                elif transaction_by_id[6] == 'pensionDina':
                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Счет Дины'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) - float(amount_difference)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
            else:
                amount_difference=float(amount)-transaction_by_id[2]

                if transaction_by_id[6] == 'pensionPapa':
                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Мой Счет'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) + float(amount_difference)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Мой Счет'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
                elif transaction_by_id[6] == 'pensionDina':
                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("select userbalance from account where description='Счет Дины'")
                            account_balance_send = cursor.fetchone()
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                    new_balance_after_expense = float(account_balance_send[0]) + float(amount_difference)

                    try:
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute(f"update account set userbalance =%s where description='Счет Дины'",
                                           (round(new_balance_after_expense, 2),))
                    except:
                        return jsonify(
                            {
                                'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

    info = collect_information()
    return info


def analytics_info(account_type, account_type_second=''):
    current_month = datetime.now().month
    info_list = []
    yearly_summary = []
    category_list = ['grocery', 'moneySend', 'utilitiesPayment', 'otherPayment', 'moneySendSnezhana', 'medicine']
    if account_type_second:
        try:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select category, sum(expensebalance), transactionyear from expenses "
                               "group by transactionmonth, category, transactionyear, account_type"
                               " having transactionmonth='%s' and account_type in(%s, %s)",
                               (current_month, account_type, account_type_second))
                information = cursor.fetchall()
        except:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select category, sum(expensebalance), transactionyear from expenses "
                               "group by transactionmonth, category, transactionyear, account_type"
                               " having transactionmonth='%s' and account_type in(%s, %s)",
                               (current_month, account_type, account_type_second))
                information = cursor.fetchall()
        for record in information:

            if record[0] == 'utilitiesPayment':
                new_info_list = {
                    "title": 'Коммунальные Платежи', "amount": record[1], "year": record[2], 'type': record[0]
                }
            elif record[0] == 'otherPayment':
                new_info_list = {
                    "title": 'Другие Платежи', "amount": record[1], "year": record[2], 'type': record[0]
                }
            elif record[0] == 'medicine':
                new_info_list = {
                    "title": 'Лекарства', "amount": record[1], "year": record[2], 'type': record[0]
                }
            elif record[0] == 'moneySendSnezhana':
                new_info_list = {
                    "title": 'Перевод Снежане', "amount": record[1], "year": record[2], 'type': record[0]
                }
            elif record[0] == 'moneySend':
                new_info_list = {
                    "title": 'Перевод Дине', "amount": record[1], "year": record[2], 'type': record[0]
                }
            elif record[0] == 'grocery':
                new_info_list = {
                    "title": 'Продукты', "amount": record[1], "year": record[2], 'type': record[0]
                }
            else:
                new_info_list = {
                    "title": record[0], "amount": record[1], "year": record[2]
                }
            info_list.append(new_info_list)
        for category in category_list:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select category, sum(expensebalance), transactionmonth, transactionyear from expenses "
                               "group by transactionmonth, category, transactionyear, account_type"
                               " having category=%s and account_type in(%s, %s)", (category, account_type, account_type_second))
                category_summary = cursor.fetchall()

            if category_summary is not None:
                for info in category_summary:
                    new_category_summary = {
                        'title': info[0], 'amount': info[1], 'month': info[2], 'year': info[3]
                    }
                    yearly_summary.append(new_category_summary)

        for record in info_list:
            for item in yearly_summary:
                if record['type'] in item['title']:
                    if 'summary' not in record:
                        record['summary'] = []
                        record['summary'].append(item)
                    else:
                        record['summary'].append(item)
    else:
        try:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select category, sum(expensebalance), transactionyear from expenses "
                               "group by transactionmonth, category, transactionyear, account_type"
                               " having transactionmonth='%s' and account_type=%s",
                               (current_month, account_type))
                information = cursor.fetchall()
        except:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select category, sum(expensebalance), transactionyear from expenses "
                               "group by transactionmonth, category, transactionyear, account_type"
                               " having transactionmonth='%s' and account_type=%s",
                               (current_month, account_type))
                information = cursor.fetchall()
        for record in information:

            if record[0] == 'utilitiesPayment':
                new_info_list = {
                    "title": 'Коммунальные Платежи', "amount": record[1], "year": record[2], 'type': record[0]
                }
            elif record[0] == 'otherPayment':
                new_info_list = {
                    "title": 'Другие Платежи', "amount": record[1], "year": record[2], 'type': record[0]
                }
            elif record[0] == 'medicine':
                new_info_list = {
                    "title": 'Лекарства', "amount": record[1], "year": record[2], 'type': record[0]
                }
            elif record[0] == 'moneySendSnezhana':
                new_info_list = {
                    "title": 'Перевод Снежане', "amount": record[1], "year": record[2], 'type': record[0]
                }
            elif record[0] == 'moneySend':
                new_info_list = {
                    "title": 'Перевод Дине', "amount": record[1], "year": record[2], 'type': record[0]
                }
            elif record[0] == 'grocery':
                new_info_list = {
                    "title": 'Продукты', "amount": record[1], "year": record[2], 'type': record[0]
                }
            else:
                new_info_list = {
                    "title": record[0], "amount": record[1], "year": record[2]
                }
            info_list.append(new_info_list)
        for category in category_list:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select category, sum(expensebalance), transactionmonth, transactionyear from expenses "
                               "group by transactionmonth, category, transactionyear, account_type"
                               " having category=%s and account_type=%s", (category, account_type))
                category_summary = cursor.fetchall()

            if category_summary is not None:
                for info in category_summary:
                    new_category_summary = {
                        'title': info[0], 'amount': info[1], 'month': info[2], 'year': info[3]
                    }
                    yearly_summary.append(new_category_summary)

        for record in info_list:
            for item in yearly_summary:
                if record['type'] in item['title']:
                    if 'summary' not in record:
                        record['summary'] = []
                        record['summary'].append(item)
                    else:
                        record['summary'].append(item)

    return {'info':info_list}


@app.route('/api/analysis_info', methods=['GET'])
@cross_origin()
def collect_info():

    info_dina= analytics_info('DinaAccount')
    info_papa= analytics_info('PapaAccount', account_type_second='SnezhanaAccount')

    return {'infoPapa':info_papa, 'infoDina': info_dina}


if __name__ == "__main__":
    app.run()
