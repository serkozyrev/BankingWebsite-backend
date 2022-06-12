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

def analytics_info(account_type, account_type_second=''):
    current_month = datetime.now().month
    info_list = []
    yearly_summary = []
    category_list = ['grocery', 'moneySend', 'utilitiesPayment', 'otherPayment', 'moneySendSnezhana', 'medicine']
    if account_type_second:
        try:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select category, sum(expensebalance), transactionyear from expense "
                               "group by transactionmonth, category, transactionyear, account_type"
                               " having transactionmonth='%s' and account_type in(%s, %s)",
                               (current_month, account_type, account_type_second))
                information = cursor.fetchall()
        except:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select category, sum(expensebalance), transactionyear from expense "
                               "group by transactionmonth, category, transactionyear, account_type"
                               " having transactionmonth='%s' and account_type in(%s, %s)",
                               (current_month, account_type, account_type_second))
                information = cursor.fetchall()
        for record in information:

            if record[0] == 'utilitiesPayment':

                new_info_list = {
                    "title": 'Utilities', "amount": round(record[1],2), "year": record[2], 'type': record[0]
                }
            elif record[0] == 'otherPayment':
                new_info_list = {
                    "title": 'Other Payment', "amount": round(record[1],2), "year": record[2], 'type': record[0]
                }
            elif record[0] == 'medicine':
                new_info_list = {
                    "title": 'Medicine', "amount": round(record[1],2), "year": record[2], 'type': record[0]
                }
            elif record[0] == 'moneySendSnezhana':
                new_info_list = {
                    "title": 'Transfer to Line of Credit', "amount": round(record[1],2), "year": record[2], 'type': record[0]
                }
            elif record[0] == 'moneySend':
                new_info_list = {
                    "title": 'Transfer to Visa', "amount": round(record[1],2), "year": record[2], 'type': record[0]
                }
            elif record[0] == 'grocery':
                new_info_list = {
                    "title": 'Grocery', "amount": round(record[1],2), "year": record[2], 'type': record[0]
                }
            else:
                new_info_list = {
                    "title": record[0], "amount": round(record[1],2), "year": record[2]
                }
            info_list.append(new_info_list)
        for category in category_list:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select category, sum(expensebalance), transactionmonth, transactionyear from expense "
                               "group by transactionmonth, category, transactionyear, account_type"
                               " having category=%s and account_type in(%s, %s)", (category, account_type, account_type_second))
                category_summary = cursor.fetchall()

            if category_summary is not None:
                for info in category_summary:
                    new_category_summary = {
                        'title': info[0], 'amount': round(info[1],2), 'month': info[2], 'year': info[3]
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
                cursor.execute("select category, sum(expensebalance), transactionyear from expense "
                               "group by transactionmonth, category, transactionyear, account_type"
                               " having transactionmonth='%s' and account_type=%s",
                               (current_month, account_type))
                information = cursor.fetchall()
        except:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select category, sum(expensebalance), transactionyear from expense "
                               "group by transactionmonth, category, transactionyear, account_type"
                               " having transactionmonth='%s' and account_type=%s",
                               (current_month, account_type))
                information = cursor.fetchall()
        for record in information:
            if record[0] == 'utilitiesPayment':

                new_info_list = {
                    "title": 'Utilities', "amount": round(record[1], 2), "year": record[2], 'type': record[0]
                }
            elif record[0] == 'otherPayment':
                new_info_list = {
                    "title": 'Other Payment', "amount": round(record[1], 2), "year": record[2], 'type': record[0]
                }
            elif record[0] == 'medicine':
                new_info_list = {
                    "title": 'Medicine', "amount": round(record[1], 2), "year": record[2], 'type': record[0]
                }
            elif record[0] == 'moneySendSnezhana':
                new_info_list = {
                    "title": 'Transfer to Line of Credit', "amount": round(record[1], 2), "year": record[2],
                    'type': record[0]
                }
            elif record[0] == 'moneySend':
                new_info_list = {
                    "title": 'Transfer to Visa', "amount": round(record[1], 2), "year": record[2], 'type': record[0]
                }
            elif record[0] == 'grocery':
                new_info_list = {
                    "title": 'Grocery', "amount": round(record[1], 2), "year": record[2], 'type': record[0]
                }
            else:
                new_info_list = {
                    "title": record[0], "amount": round(record[1], 2), "year": record[2]
                }
            info_list.append(new_info_list)
        for category in category_list:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select category, sum(expensebalance), transactionmonth, transactionyear from expense "
                               "group by transactionmonth, category, transactionyear, account_type"
                               " having category=%s and account_type=%s", (category, account_type))
                category_summary = cursor.fetchall()

            if category_summary is not None:
                for info in category_summary:
                    new_category_summary = {
                        'title': info[0], 'amount': round(info[1],2), 'month': info[2], 'year': info[3]
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