#
import unittest
import requests
import sqlite3
import json
import os
import matplotlib.pyplot as plt

our_dates = ['2020-04-02', '2020-04-04', '2020-04-06', '2020-04-08','2020-04-10','2020-04-12','2020-04-14', '2020-04-16', '2020-04-18', '2020-04-20','2020-04-22','2020-04-24', '2020-04-26', '2020-04-28','2020-04-30','2020-05-02', '2020-05-04', '2020-05-06', '2020-05-08','2020-05-10','2020-05-12','2020-05-14', '2020-05-16', '2020-05-18', '2020-05-20','2020-05-22','2020-05-24', '2020-05-26', '2020-05-28','2020-05-30', '2020-06-02', '2020-06-04', '2020-06-06', '2020-06-08','2020-06-10','2020-06-12','2020-06-14', '2020-06-16', '2020-06-18', '2020-06-20','2020-06-22','2020-06-24', '2020-06-26', '2020-06-28','2020-06-30','2020-07-02', '2020-07-04', '2020-07-06', '2020-07-08','2020-07-10','2020-07-12','2020-07-14', '2020-07-16', '2020-07-18', '2020-07-20','2020-07-22','2020-07-24', '2020-07-26', '2020-07-28','2020-07-30','2020-08-02', '2020-08-04', '2020-08-06', '2020-08-08','2020-08-10','2020-08-12','2020-08-14', '2020-08-16', '2020-08-18', '2020-08-20','2020-08-22','2020-08-24', '2020-08-26', '2020-08-28','2020-08-30', '2020-09-02', '2020-09-04', '2020-09-06', '2020-09-08','2020-09-10','2020-09-12','2020-09-14', '2020-09-16', '2020-09-18', '2020-09-20','2020-09-22','2020-09-24', '2020-09-26', '2020-09-28','2020-09-30','2020-10-02', '2020-10-04', '2020-10-06', '2020-10-08','2020-10-10','2020-10-12','2020-10-14', '2020-10-16', '2020-10-18', '2020-10-20','2020-10-22','2020-10-24', '2020-10-26', '2020-10-28','2020-10-30','2020-11-02', '2020-11-04', '2020-11-06', '2020-11-08','2020-11-10','2020-11-12','2020-11-14', '2020-11-16', '2020-11-18', '2020-11-20','2020-11-22','2020-11-24', '2020-11-26', '2020-11-28','2020-11-30', '2020-10-02', '2020-12-04', '2020-12-06', '2020-12-08','2020-12-10','2020-12-12','2020-12-14', '2020-12-16', '2020-12-18', '2020-12-20','2020-12-22','2020-12-24', '2020-12-26', '2020-12-28','2020-12-30']

# april, july, october, september --> all the dates

our_states = ['Michigan', 'California', 'Colorado', 'Florida', 'Illinois', 'Ohio', 'Texas', 'Massachusetts', 'Georgia', 'Hawaii']

def get_data(region, date_iso):
    url = f' http://api.weatherstack.com/historical?access_key=c94d102ae8f92a29c04bdeb3a7b41a82&query={region}&historical_date={date_iso}&hourly=1'
    r = requests.get(url)
    r_text = r.text
    data = json.loads(r_text)
    return data


# x =get_data('Detroit', '2020-04-02')
# print(x)

# for states in our_states:
#     test_data = get_data(states, our_states)
#     print(test_data)


def get_specific_data(region, dates_list):

    big_dict = {}
    for day in dates_list:
        info_list = []
        data = get_data(region, day)
        date = data['historical'][day]['date']
        state = data['location']['region']
        avg_temp = data['historical'][day]['avgtemp']
        temp = data['historical'][day]['hourly'][0]['temperature']
        info_list.append(state)
        info_list.append(avg_temp)
        info_list.append(temp)
        big_dict[date] = info_list

    # print(big_dict)

    return big_dict


# get_specific_data('Detroit', ['2020-04-02', '2020-04-04', '2020-04-06', '2020-04-08','2020-04-10','2020-04-12','2020-04-14', '2020-04-16', '2020-04-18', '2020-04-20','2020-04-22','2020-04-24', '2020-04-26', '2020-04-28','2020-04-30','2020-05-02', '2020-05-04', '2020-05-06'] )

# All the things for database

def setUpDatabase(database_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+database_name)
    cur = conn.cursor()
    return cur, conn


# Table for weather info

def create_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Temperature (date DATE PRIMARY KEY, state TEXT, avg_temp INTEGER, temp INTEGER)')
    conn.commit()

def check_rows(cur, conn):
    row_num = 0
    cur.execute('SELECT * from Temperature')
    row_num = cur.fetchall()
    return len(row_num)

def addition_data(data_dict, cur, conn):
    curr_rows = check_rows(cur,conn)
    target_rows = curr_rows + 25
    if target_rows > len(data_dict):
        target_rows = len(data_dict)
    data_list = list(data_dict.items())
    for number in range(curr_rows, target_rows):
        date, info_list = data_list[number]
        date_value = date
        state = info_list[0]
        avg_temp = info_list[1]
        temp = info_list[2]
        cur.execute('INSERT OR IGNORE INTO Temperature (date, state, avg_temp, temp) values (?,?,?,?)', (date_value, state, avg_temp, temp))
    conn.commit()

def main(database_name, region, date_list):
    full_data = get_specific_data(region, date_list)
    cur, conn = setUpDatabase(database_name)
    create_table(cur, conn)
    addition_data(full_data, cur, conn)

main('Covid_Temp_Animals', 'Detroit', our_dates)