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

def single_record():
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute('select * from bloodpressure order by pressureyear desc, pressuremonth collate numeric_value desc,pressureday desc,'
                       '  timeofmeasure desc')
        bloodpressure_list = cursor.fetchall()
    bloodpressures_list = []
    for item in bloodpressure_list:
        single_record = {
            'id': item[0], 'day': item[1], 'month': item[2], 'year': item[3], 'highlevel': item[4],
            'lowlevel': item[5], 'pulse': item[6], 'description': item[7], 'time': item[10]
        }
        bloodpressures_list.append(single_record)
    return {'pressure': bloodpressures_list}