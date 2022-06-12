from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from datetime import datetime
from database import Database
from database import CursorFromConnectionFromPool
from flask_cors import CORS, cross_origin
from routes.edit_record import adding_edited_record
from routes.get_record_by_id import get_by_id_info
from routes.account_info import provide_account_info
from routes.record_delete_operation import delete
from routes.copy_operation import copy
from routes.add_record import add
from routes.get_expenses import expenses
from routes.information import collect_information
from routes.selected_pressure import single_record
from routes.analytics import analytics_info

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


@app.route('/api/bloodpressure', methods=["GET", "POST"])
@cross_origin()
def get_all_bloodpres():
    if request.method == "POST":
        date = request.json["date"]
        date_splited = date.split('-')
        day = date_splited[2]
        month = date_splited[1][-1:]
        year = date_splited[0]
        highlevel = request.json["highlevel"]
        lowlevel = request.json["lowlevel"]
        description = request.json["description"]
        pulse = request.json["pulse"]
        timeline = request.json["timeline"]

        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('insert into bloodpressure(pressureday, pressuremonth, pressureyear,highlevel,'
                           ' lowlevel,pulse, description, timeofmeasure) values(%s, %s, %s, %s, %s,%s, %s, %s)',
                           (day, month, year, highlevel, lowlevel, pulse, description, timeline))

        bloodpressure_list = single_record()
        return bloodpressure_list
    else:
        bloodpressure_list = single_record()
        return bloodpressure_list


@app.route('/api/bloodpressure/edit', methods=['PATCH'])
@cross_origin()
def edit_bloodpressure():
    transid = request.json['id']
    date = request.json["date"]
    date_splited = date.split('-')
    day = date_splited[2]
    month = date_splited[1][-1:]
    year = date_splited[0]
    highlevel = request.json["highlevel"]
    lowlevel = request.json["lowlevel"]
    description = request.json["description"]
    pulse = request.json["pulse"]
    timeline = request.json["timeline"]

    with CursorFromConnectionFromPool() as cursor:
        cursor.execute('select * from bloodpressure where pressureid=%s', (transid,))
        transaction_by_id = cursor.fetchone()

    if transaction_by_id:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('update bloodpressure set pressureday=%s, pressuremonth=%s, pressureyear=%s, highlevel=%s,'
                           ' lowlevel=%s, pulse=%s, description=%s, timeofmeasure=%s where pressureid=%s',
                           (day, month, year, highlevel, lowlevel, pulse, description, timeline, transid))
        bloodpressure_list = single_record()
        return bloodpressure_list


@app.route('/api/get_pressure_by_id', methods=['POST'])
@cross_origin()
def get_pressure_by_id():
    record_id = request.json['id']
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute('select * from bloodpressure where pressureid=%s', (record_id,))
        transaction_by_id = cursor.fetchone()

    if transaction_by_id:
        if int(transaction_by_id[2]) < 10:
            date = transaction_by_id[3] + '-0' + transaction_by_id[2] + '-' + transaction_by_id[1]
        else:
            date = transaction_by_id[3] + '-' + transaction_by_id[2] + '-' + transaction_by_id[1]
        selected_record = {
            'date': date, "highlevel": transaction_by_id[4], 'lowlevel': transaction_by_id[5],
            'pulse': transaction_by_id[6], 'description': transaction_by_id[7], 'time': transaction_by_id[10]
        }

        return {'pressure': selected_record}


@app.route('/api/expenses', methods=['GET'])
@cross_origin()
def get_all_expenses():
    expense_list = expenses()

    return expense_list


@app.route('/api/revenues', methods=['GET'])
@cross_origin()
def get_all_revenue():
    try:
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                'select * from revenues order by transactionmonth desc,transactionday desc,  transactionyear desc')
            revenues = cursor.fetchall()
    except:
        return jsonify({'message': 'Не получилось получить данные о доходах, попробуйте позже'})

    revenues_list = []

    for revenue in revenues:
        new_revenue = {
            'id': revenue[0], 'description': revenue[1], 'amount': f'{revenue[2]:,}',
            'day': revenue[3], 'month': revenue[4], 'year': revenue[5], 'type': revenue[7]
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
    day = date_splited[2]
    month = date_splited[1][-1:]
    year = date_splited[0]
    dollars = float(rate) * float(amount)

    add(transaction_type, description, amount, day, month, year, category, rate, account_type, dollars)

    info = collect_information()
    return info


@app.route('/api/copyrecord', methods=['POST'])
@cross_origin()
def copy_record():
    transaction_id = request.json["id"]
    transaction_type = request.json["type"]
    date = datetime.today().strftime('%Y-%m-%d')

    date_splited = date.split('-')
    copy_day = date_splited[2]
    copy_month = date_splited[1][-1:]
    copy_year = date_splited[0]

    copy(transaction_id, transaction_type, copy_day, copy_month, copy_year)

    info = collect_information()

    return info


@app.route('/api/deleterecord', methods=['POST'])
@cross_origin()
def delete_record():
    transaction_id = request.json["id"]
    transaction_type = request.json["type"]

    delete(transaction_id, transaction_type)

    info = collect_information()

    return info


@app.route('/api/account', methods=['GET'])
@cross_origin()
def get_account_info():
    account_info = provide_account_info()
    return account_info


@app.route('/api/get_by_id', methods=['POST'])
@cross_origin()
def get_by_id():
    transid = request.json['id']
    transtype = request.json['type']
    record_info = get_by_id_info(transid, transtype)
    return record_info


@app.route('/api/search', methods=['POST'])
@cross_origin()
def search():
    description_field = request.json["description"]
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute(
            f"select * from expenses where lower(description) like '%{description_field}%' order by transactionmonth desc,transactionday desc,  transactionyear desc")
        all_records_found = cursor.fetchall()

    expenses_list = []
    expenses_list_dina = []

    for record in all_records_found:
        if record[9] == 'DinaAccount':
            new_expense_dina = {
                'id': record[0], 'description': record[1], 'amount': f'{record[2]:,}',
                'day': record[3], 'month': record[4], 'year': record[5],
                'amountindollar': f'{record[6]:,}', 'category': record[7], 'type': record[8]
            }
            expenses_list_dina.append(new_expense_dina)
        else:
            new_expense = {
                'id': record[0], 'description': record[1], 'amount': f'{record[2]:,}',
                'day': record[3], 'month': record[4], 'year': record[5],
                'amountindollar': f'{record[6]:,}', 'category': record[7], 'type': record[8]
            }
            expenses_list.append(new_expense)

    return {'dinaExpense': expenses_list_dina, 'expenses': expenses_list}


@app.route('/api/editrecord', methods=['PATCH'])
@cross_origin()
def edit_record():
    transid = request.json['id']
    transtype = request.json['type']
    description = request.json["description"]
    amount = request.json["amount"]
    date = request.json["date"]
    category = request.json["category"]
    rate = request.json["rate"]
    account = request.json["accountType"]

    date_splited = date.split('-')
    day = date_splited[2]
    month = date_splited[1][-1:]
    year = date_splited[0]
    result_new = ''
    result_old = ''
    adding_edited_record(transid, transtype, description, amount, day, month, year, category, rate, account, result_new,
                         result_old)

    info = collect_information()

    return info


@app.route('/api/analysis_info', methods=['GET'])
@cross_origin()
def collect_info():
    info_dina = analytics_info('DinaAccount')
    info_papa = analytics_info('PapaAccount', account_type_second='SnezhanaAccount')
    return {'infoPapa': info_papa, 'infoDina': info_dina}


if __name__ == "__main__":
    app.run(debug=True)