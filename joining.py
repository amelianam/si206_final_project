def connect_temp_and_covid_by_date(cur, conn):
    cur.execute('SELECT Temperature.date, Temperature.state, Temperature.avg_temp, Covid.date, Covid.state, Covid.cases FROM Covid JOIN Temperature ON Temp.date = Covid.date')
    list_of_matches = cur.fetchall()
    return list_of_matches


# def calculate_SOMETHING(list_of_matches):
#     calculate_something_here