import json
import unittest
import os
import requests
import sqlite3
import matplotlib
import matplotlib.pyplot as plt

#state code should be two letter, lowercase
#date_iso should be year, month, day 



spring = ['03', '04', '05']
summer = ['06', '07', '08']
fall = ['09', '10', '11']
winter = ['12', '01', '02']

our_dates = ['2020-04-02', '2020-04-04', '2020-04-06', '2020-04-08','2020-04-10','2020-04-12','2020-04-14', '2020-04-16', '2020-04-18', '2020-04-20','2020-04-22','2020-04-24', '2020-04-26', '2020-04-28','2020-04-30','2020-05-02', '2020-05-04', '2020-05-06', '2020-05-08','2020-05-10','2020-05-12','2020-05-14', '2020-05-16', '2020-05-18', '2020-05-20','2020-05-22','2020-05-24', '2020-05-26', '2020-05-28','2020-05-30', '2020-06-02', '2020-06-04', '2020-06-06', '2020-06-08','2020-06-10','2020-06-12','2020-06-14', '2020-06-16', '2020-06-18', '2020-06-20','2020-06-22','2020-06-24', '2020-06-26', '2020-06-28','2020-06-30','2020-07-02', '2020-07-04', '2020-07-06', '2020-07-08','2020-07-10','2020-07-12','2020-07-14', '2020-07-16', '2020-07-18', '2020-07-20','2020-07-22','2020-07-24', '2020-07-26', '2020-07-28','2020-07-30','2020-08-02', '2020-08-04', '2020-08-06', '2020-08-08','2020-08-10','2020-08-12','2020-08-14', '2020-08-16', '2020-08-18', '2020-08-20','2020-08-22','2020-08-24', '2020-08-26', '2020-08-28','2020-08-30', '2020-09-02', '2020-09-04', '2020-09-06', '2020-09-08','2020-09-10','2020-09-12','2020-09-14', '2020-09-16', '2020-09-18', '2020-09-20','2020-09-22','2020-09-24', '2020-09-26', '2020-09-28','2020-09-30','2020-10-02', '2020-10-04', '2020-10-06', '2020-10-08','2020-10-10','2020-10-12','2020-10-14', '2020-10-16', '2020-10-18', '2020-10-20','2020-10-22','2020-10-24', '2020-10-26', '2020-10-28','2020-10-30','2020-11-02', '2020-11-04', '2020-11-06', '2020-11-08','2020-11-10','2020-11-12','2020-11-14', '2020-11-16', '2020-11-18', '2020-11-20','2020-11-22','2020-11-24', '2020-11-26', '2020-11-28','2020-11-30', '2020-10-02', '2020-12-04', '2020-12-06', '2020-12-08','2020-12-10','2020-12-12','2020-12-14', '2020-12-16', '2020-12-18', '2020-12-20','2020-12-22','2020-12-24', '2020-12-26', '2020-12-28','2020-12-30' ]

state_list = ['mi', 'ca', 'co', 'fl']

spring = ['03', '04', '05']
summer = ['06', '07', '08']
fall = ['09', '10', '11']
winter = ['12', '01', '02']

def get_all_data (state_code, date_iso):
    url = f' https://api.covidtracking.com/v2/states/{state_code}/{date_iso}/simple.json'
    r = requests.get(url)
    r_text = r.text
    data = json.loads(r_text)
    return data


def get_important_data(big_data):
    state_date_cases_list = []
    if 'error' in big_data:
        return []
    else:
        date = big_data["data"]['date']
        state = big_data["data"]['state']
        cases = big_data["data"]['cases']['total']
        state_date_cases_list.append(state)
        state_date_cases_list.append(date)
        state_date_cases_list.append(cases)
        return state_date_cases_list

def single_date_data_dictionary(state, date_list):
    single_date_data_dict = {}
    for date in date_list:
        small_dict = {}
        data = get_all_data(state, date)
        important_data = get_important_data(data)
        if len(important_data) != 3:
            small_dict[date] = "no data available for this date"
        else:
            cases = important_data[2]
            small_dict[state] = cases
        if date not in single_date_data_dict:
            single_date_data_dict[date] = small_dict
        else:
            if state not in single_date_data_dict.values():
                single_date_data_dict[date].update(small_dict)
    return single_date_data_dict


# def list_of_date_dicts_for_all_states_given(state_list, dates_list):
#     list_of_date_dicts_for_many_states = []
#     for state in state_list:
#         list_of_date_dicts_for_many_states.append(single_date_data_dictionary(state, dates_list))
#     return list_of_date_dicts_for_many_states



#DATABASE STUFF

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn



# # # CREATE TABLE FOR EMPLOYEE INFORMATION IN DATABASE AND ADD INFORMATION
def create_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Covid (date DATE PRIMARY KEY, state TEXT, cases INTEGER)')
    conn.commit()

def check_rows(cur, conn):
    row_num = 0
    cur.execute('SELECT * from Covid')
    row_num = cur.fetchall()
    return len(row_num)

def add_data_to_table(big_data_dict, cur, conn):
    current_rows = check_rows(cur, conn)
    target_rows = current_rows + 25
    if target_rows > len(big_data_dict):
        target_rows = len(big_data_dict)
    data_list = list(big_data_dict.items())
    for num in range(current_rows, target_rows):
        date, small_dict = data_list[num]
        date_val = date
        for state, cases in small_dict.items():
            state_val = state
            cases_value = cases
            cur.execute('INSERT OR IGNORE INTO Covid (date, state, cases) values (?,?,?)', (date_val, state_val, cases_value))
    conn.commit()
# [current_rows: target_rows] THIS NEEDS TO BE ADDED TO LIMIT DATA TO 25 SOMEWHERE 


# def calculate_SOMETHING(list_of_matches):
#     calculate_something_here



def main(database_name, state, date_list):
    full_data_in_list = single_date_data_dictionary(state, date_list)
    cur, conn = setUpDatabase(database_name)
    create_table(cur, conn)
    add_data_to_table(full_data_in_list, cur, conn)
    connect_temp_and_covid_by_date(cur, conn)


# test = single_date_data_dictionary('mi', our_dates)
# print('TEST FULL DICT ')
# print(test)

# github link https://github.com/amelianam/si206_final_project.git

# # TASK 2: GET TEMP AND CASES INFO JOINED
def connect_temp_and_covid_by_date(cur, conn):
    cur.execute('SELECT Temperature.date, Temperature.avg_temp, Covid.cases FROM Covid JOIN Temperature ON Temperature.date = Covid.date')
    list_of_matches = cur.fetchall()
    for tup in list_of_matches:
        date = tup[0]
        avg_temp = tup[1]
        cases = tup[2]
        month = date.split('-')[1]
        fall_case_total = 0
        winter_case_total = 0
        spring_case_total = 0
        summer_case_total = 0
        state_cases_season_dict = {}
        if month in spring:
            spring_case_total += cases
            season = 'spring'
            if season not in state_cases_season_dict.items():
                state_cases_season_dict[season] = spring_case_total
            else:
                state_cases_season_dict[season].update(spring_case_total)
        elif month in summer:
            summer_case_total += cases
            season = 'summer'
            if season not in state_cases_season_dict.items():
                state_cases_season_dict[season] = summer_case_total
            else:
                state_cases_season_dict[season].update(summer_case_total)
        elif month in winter:
            winter_case_total += cases
            season = 'winter'
            if season not in state_cases_season_dict.items():
                state_cases_season_dict[season] = winter_case_total
            else:
                state_cases_season_dict[season].update(winter_case_total)
        else:
            fall_case_total += cases
            season = 'fall'
            if season not in state_cases_season_dict.items():
                state_cases_season_dict[season] = fall_case_total
            else:
                state_cases_season_dict[season].update(fall_case_total)
    print(state_cases_season_dict)
    return state_cases_season_dict



main('Covid_Temp_Animals.db', 'mi', our_dates)





spring = ['03', '04', '05']
summer = ['06', '07', '08']
fall = ['09', '10', '11']
winter = ['12', '01', '02']


def cases_by_season_per_state(full_list_of_dicts):
    state_cases_season_dict = {}
    fall_case_total = 0
    winter_case_total = 0
    spring_case_total = 0
    summer_case_total = 0
    for dict in full_list_of_dicts:
        for state, small_dict in dict.items():
            for date, cases in small_dict.items():
                month = date.split('-')[1]
                small_dict = {}
                if month in spring:
                    spring_case_total += cases
                    season = 'spring'
                    small_dict[season] = spring_case_total
                elif month in summer:
                    summer_case_total += cases
                    season = 'summer'
                    small_dict[season] = summer_case_total
                elif month in winter:
                    winter_case_total += cases
                    season = 'winter'
                    small_dict[season] = winter_case_total
                else:
                    fall_case_total += cases
                    season = 'fall'
                    small_dict[season] = fall_case_total
                if state not in state_cases_season_dict:
                    state_cases_season_dict[state] = small_dict
                else:
                    if season not in state_cases_season_dict.values():
                        state_cases_season_dict[state].update(small_dict)
    return state_cases_season_dict