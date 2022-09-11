import gspread
from oauth2client.service_account import ServiceAccountCredentials
import psycopg2
import pandas as pd
import os
import time
import configparser
import requests
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine
from threading import Thread
import keyboard




# чтение начальных параметров из config.ini
def config():
    config = configparser.ConfigParser()
    config.read(os.path.dirname(__file__) + "/creds/config.ini")
    credpath = config['default']['credpath']
    dbhost = config['default']['dbhost']
    dbuser = config['default']['dbuser']
    dbpass = config['default']['dbpass']
    database = config['default']['database']
    UpdateTime = config['default']['UpdateTime']
    sql_al = config['default']['sql']

    return credpath, dbhost, dbuser, dbpass, database, UpdateTime, sql_al

# инициализация 1 запуска


# проверка соединения к googlesheet
def GoogleSheetsConnect():
    SERVICE_ACCOUNT_FILE = os.path.dirname(__file__) + config()[0]
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)
        print('Соединение с Гугл таблицей установлено')
    except:
        print('Не удалось открыть Гугл таблицу')
        quit()
    return client


# проверка соединения к test-kanal-db (можно через орм peewee но раз это тест то использовать не будем
def dbconnection():
    dbhost = config()[1]
    dbuser = config()[2]
    dbpass = config()[3]
    database = config()[4]

    try:
        conn = psycopg2.connect(dbname=database, user=dbuser, host=dbhost, password=dbpass, port='5432')
        cursor = conn.cursor()
        print('Соединение с БД установлено')
    except:
        print('Не удалось установить соеднинение с базой данных')
    return conn, cursor


# проверка соединения к cbr.ru и получение данных на дату из cbr.ru
def ReadDollar(date):

    req = requests.get('http://www.cbr.ru/scripts/XML_daily.asp?date_req=' + date)
    tree = ET.fromstring(req.content)
    #print(tree)
    for element in tree.findall("Valute"):
        if element.attrib == {'ID': 'R01235'}:
            #name = element.find('Name')
            curs = element.find('Value')
            #print(f'{name.text}: {curs.text}')
    return curs.text

# получение данных из БД
def ReadDB():
    info_sql = 'SELECT * FROM test'
    cursor = dbconnection()[1]
    cursor.execute(info_sql)
    data = pd.DataFrame(cursor.fetchall())
    #count_result = cursor.fetchone()
    return data

def GetCountDB():
    info_count_sql = 'SELECT COUNT(*) FROM test'
    cursor = dbconnection()[1]
    cursor.execute(info_count_sql)
    count_result = cursor.fetchone()
    num_rows = count_result[0]
    return num_rows

# корректировка формата флоат
def toFixed(f: float, n=0):
    a, b = str(f).split('.')
    return '{}.{}{}'.format(a, b[:n], '0'*(n-len(b)))

# чтение данных из googlesheet добавление стоимости в рублях в таблицу
def ReadSheets(SheetName):
    client = GoogleSheetsConnect()
    sheet = client.open(SheetName).sheet1
    data = pd.DataFrame(sheet.get_all_records())
    datalen=len(sheet.get_all_records())
    #data["Стоимость, руб"] = []
    #data.insert(4, "Стоимость,руб", "")

    i = 0
    while (i <  datalen):
        sum_r = ReadDollar(data.iloc[i,3])
        sum_r = toFixed(float(sum_r.replace(",", "."))*data.iloc[i,2], 2)
        data.loc[i,4] = sum_r
        #print(sum_r)
        i=i+1
    #data.rename(columns={'4': 'Стоимость,руб'})
    data.rename(columns={4: 'Стоимость,руб'}, inplace=True)
    #print (data)
    return data

# запись данных в test-kanal-db
def InsertDB():
    dataSH = ReadSheets('test')
    #dataDB = ReadDB()
    #print(dataSH)
    #print(dataDB)
    engine = create_engine(config()[6])
    dataSH.to_sql('test', con=engine, if_exists='replace')
    #print(engine.execute("SELECT * FROM test").fetchall())

def main():
    time_delay = config()[5]
    time_start = time.time()
    while True:
        if (not int(time_start) % int(time_delay)*60):
            try:
                InsertDB()
            except:
                print('программа прекратила работу')
                quit()


if __name__ == '__main__':

    main()