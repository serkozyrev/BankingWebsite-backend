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

def get_by_id_info(transid,transtype):
    if transtype == 'expense':
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from expense where expenseid=%s', (transid,))
            transaction_by_id = cursor.fetchone()

        expense_transaction_info = {
            'id': transaction_by_id[0], 'description': transaction_by_id[1], 'amount': transaction_by_id[2],
            'day': transaction_by_id[3], 'month': transaction_by_id[4], 'year': transaction_by_id[5],
            'amountindollars': transaction_by_id[6], 'category': transaction_by_id[7], 'type': transtype,
            'accountType': transaction_by_id[9]
        }
        return jsonify({'expense': expense_transaction_info})
    elif transtype == 'revenue':
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from revenue where revenueid = %s', (transid,))
            revenue_transaction_by_id = cursor.fetchone()

        revenue_transaction_info = {
            'id': revenue_transaction_by_id[0], 'description': revenue_transaction_by_id[1],
            'amount': revenue_transaction_by_id[2],
            'day': revenue_transaction_by_id[3], 'month': revenue_transaction_by_id[4],
            'year': revenue_transaction_by_id[5], 'category': revenue_transaction_by_id[6], 'type': transtype
        }
        return jsonify({'revenue': revenue_transaction_info})