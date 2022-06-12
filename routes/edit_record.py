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

def adding_edited_record(transid, transtype, description, amount, day,month,year, category, rate, account,result_new, result_old):
    if transtype == 'expense':
        dollars = float(rate) * float(amount)
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from expenses where expenseid = %s', (transid,))
            transaction_by_id = cursor.fetchone()
        if transaction_by_id:
            if account != transaction_by_id[9]:
                if account == 'DinaAccount':
                    result_new = 'Счет Дины'
                elif account == 'PapaAccount':
                    result_new = 'Мой Счет'
                elif account == 'SnezhanaAccount':
                    result_new = 'Счет Снежаны'
                if transaction_by_id[9] == 'DinaAccount':
                    result_old = 'Счет Дины'
                elif transaction_by_id[9] == 'PapaAccount':
                    result_old = 'Мой Счет'
                elif transaction_by_id[9] == 'SnezhanaAccount':
                    result_old = 'Счет Снежаны'
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute('update expenses set description=%s, expensebalance=%s, transactionday=%s, '
                                   'transactionmonth=%s, transactionyear=%s,amountindollars=%s, category=%s,'
                                   ' account_type=%s where expenseid=%s',
                                   (description, amount, day, month, year, round(dollars, 2), category, account,
                                    transid))

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description=%s", (result_new,))
                        account_balance_new = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute("select userbalance from account where description=%s", (result_old,))
                        account_balance_previous = cursor.fetchone()
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})
                print(account_balance_previous[0], account_balance_new[0])
                new_balance_previous_account = account_balance_previous[0]+float(amount)
                new_balance_new_account = account_balance_new[0]-float(amount)

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description=%s",
                                       (round(new_balance_previous_account, 2), result_old))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

                try:
                    with CursorFromConnectionFromPool() as cursor:
                        cursor.execute(f"update account set userbalance =%s where description=%s",
                                       (round(new_balance_new_account, 2), result_new))
                except:
                    return jsonify(
                        {'message': 'Не получилось получить данные о балансе с аккаунта "Мой Счет", попробуйте позже'})

            else:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute('update expenses set description=%s, expensebalance=%s, transactionday=%s, '
                                   'transactionmonth=%s, transactionyear=%s,amountindollars=%s, category=%s, account_type=%s where expenseid=%s',
                                   (description, amount, day, month, year, round(dollars, 2), category, account,
                                    transid))
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