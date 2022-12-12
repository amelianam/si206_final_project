import unittest
import requests
import sqlite3
import json
import os
import matplotlib.pyplot as plt


# get the data as json file - search on original_receive_date, 1 month date range and run getData multiple times for every month
def getData(search, dateStart, dateEnd, limitnum):
    url = f'https://api.fda.gov/animalandveterinary/event.json?search={search}:[{dateStart}+TO+{dateEnd}]&limit={limitnum}'
    r = requests.get(url)
    r_text = r.text
    data = json.loads(r_text)
    return data

 
#  Filter data with list of original_receive_date
#["results"][0]["origina_receive_date"]
def filterData(jsonData):
    list_of_dates = []
    
    # remove the first dictionary and only get the results dictionary
    loopingList = jsonData["results"]

    # loop through loopingList and get the original_receive_date and append to list
    for cases in loopingList:
        list_of_dates.append(cases["original_receive_date"])
    

    # return the list of data
    return list_of_dates


#ALL DATABASE STUFF

# we want to get a dictionary with key value date and value # of cases -- use .get( , ) + 1
def makeDict(dateList, modifyDict):



    for date in dateList:
        modifyDict[date] = modifyDict.get(date, 0) + 1
    
    return modifyDict



def setupdb(dbname):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+dbname)
    cur = conn.cursor()
    return cur, conn

   
def makedb(cur, conn):
     #create table
    cur.execute("CREATE TABLE IF NOT EXISTS Vetinary (dates TEXT, cases INTEGER)")
    conn.commit()
    
# store into database : 25 at a time 1 column is date and 1 column is # of cases from 4 different months --> April, July, October, December 202
    
#get num of rows
def rowPosition(cur, conn):
    row_num = 0
    cur.execute('SELECT * from Vetinary')
    row_num = cur.fetchall()
    return len(row_num)

#check 25 at a time
def storedb(cur, conn, dataDict):
    
    curr_rows = rowPosition(cur,conn)
    target_rows = curr_rows + 25
    if target_rows > len(dataDict):
        target_rows = len(dataDict)
    
    # list of dictionary items
    data_list = list(dataDict.items())
    

    # Add to database
    for number in range(curr_rows, target_rows):
        theKey = data_list[number][0]
        #change the format of date
        formattedKey = theKey[:4] + "-" + theKey[4:6] + "-" + theKey[6:]

        theValue = data_list[number][1]
       
        cur.execute("INSERT OR IGNORE INTO Vetinary (dates, cases) VALUES (?,?)", (formattedKey, theValue))
        
    conn.commit()


def get_graph_data(cur, conn):
    cur.execute('SELECT Temperature.date, Temperature.avg_temp, Temperature.temp, Vetinary.cases FROM Temperature JOIN Vetinary ON Temperature.date = Vetinary.dates')
    list_of_matches = cur.fetchall()
   
    differences = [] #list of x axis
    cases = [] #list of y axis
    for day in list_of_matches:
        # create list with [abs value of differences] and one list with [cases] then match it to a dictionary with key as the month
        difference_value = abs(day[1] - day[2])
        difference_value = round(difference_value, 2)
        differences.append(difference_value)

        #create list of all cases
        cases.append(day[3])

    #create return list    
    return_list = [differences,cases]
 
    return return_list




def visualization1(data_list):
    # get x,y data
    xaxis = data_list[0]
    yaxis = data_list[1]
    
    #graph figure
    figure = plt.figure(figsize= (10,6))

    for num in range(len(xaxis)):
        plt.scatter(xaxis[num], yaxis[num], s=30)
    
    plt.text(10, 330, "*Color does not have\nany meaning,\nsimply added\nfor visual purposes", weight = 'semibold')
    plt.xlabel("Daily Temperature Difference(Degrees Fahrenheit)")
    plt.ylabel("Number of Veterinary Cases")
    plt.title("Number of Veterinary Cases \n based on the\nDaily Temperature Differences")
    plt.show()

    
def get_graph2_data(cur, conn):
    cur.execute('SELECT Temperature.date, Temperature.avg_temp, Vetinary.cases FROM Temperature JOIN Vetinary ON Temperature.date = Vetinary.dates')
    list_of_matches = cur.fetchall()
    
    april_list = list(list_of_matches[0:30])
    july_list = list(list_of_matches[30:61])
    oct_list = list(list_of_matches[61:92])
    dec_list = list(list_of_matches[92:123])
    
    loop_list = [april_list, july_list, oct_list, dec_list]

    temp_list = []
    cases_list = []
    for month in loop_list:
        temp_sum = 0
        cases_sum = 0
        for days in month:
            temp_sum += days[1]
            cases_sum += days[2]
        
        temp_list.append(round(temp_sum / len(month), 2))
        cases_list.append(round(cases_sum / len(month), 2))
    
    return_list = [temp_list, cases_list]
    return return_list



def visualization2(list_data):
    #get x,y data, colors, and months
    months_list = ['April = Spring', 'July = Summer', 'October = Fall', 'December = Winter']
    x_data = list_data[0]
    y_data = list_data[1]
    color_list = ['magenta', 'springgreen', 'orangered', 'c']

    # make figure
    figure = plt.figure(figsize= (10,6))
    for num in range(len(months_list)):
        plt.scatter(x_data[num], y_data[num], s=120, color = color_list[num], label = months_list[num])
        plt.annotate(y_data[num], (x_data[num], y_data[num] + 1), horizontalalignment='center')
    plt.xlabel("Average Temperature (Degrees Fahrenheit)")
    plt.ylabel("Average Number of Veterinary Cases")
    plt.title("Number of Veterinary Cases \n based on Average Temperature for Each Season")
    plt.legend()
    plt.show()

def create_file(file_name, data_dictionary):
    with open(file_name, 'w') as convert_file:
        convert_file.write(json.dumps(data_dictionary))

# main function
if __name__ == '__main__':
    databaseDict = {}
    
    dateList = ["20200401", "20200402", "20200403", "20200404", "20200405", "20200406", "20200407", "20200408", "20200409", "20200410", "20200411", "20200412", "20200413", "20200414", "20200415", "20200416", "20200417", "20200418", "20200419", "20200420", "20200421", "20200422", "20200423", "20200424", "20200425", "20200426", "20200427", "20200428", "20200429", "20200430", "20200701", "20200702", "20200703", "20200704", "20200705", "20200706", "20200707", "20200708", "20200709", "20200710", "20200711", "20200712", "20200713", "20200714", "20200715", "20200716", "20200717", "20200718", "20200719", "20200720", "20200721", "20200722", "20200723", "20200724", "20200725", "20200726", "20200727", "20200728", "20200729", "20200730", "20200731", "20201001", "20201002", "20201003", "20201004", "20201005", "20201006", "20201007", "20201008", "20201009", "20201010", "20201011", "20201012", "20201013", "20201014", "20201015", "20201016", "20201017", "20201018", "20201019", "20201020", "20201021", "20201022", "20201023", "20201024", "20201025", "20201026", "20201027", "20201028", "20201029", "20201030", "20201031", "20201201", "20201202", "20201203", "20201204", "20201205", "20201206", "20201207", "20201208", "20201209", "20201210", "20201211", "20201212", "20201213", "20201214", "20201215", "20201216", "20201217", "20201218", "20201219", "20201220", "20201221", "20201222", "20201223", "20201224", "20201225", "20201226", "20201227", "20201228", "20201229", "20201230", "20201231"]
   
    # Get each string and change the format through indexing first 4 and adding -, index the 5 and 6 and add -, and add the last 2
   
    #should loop through initial data for certain number of dates
    for date in dateList:
        initialData = getData("original_receive_date", date, date, "1000")
        filteredData = filterData(initialData)
        databaseDict = makeDict(filteredData, databaseDict)
    
    #make the connection
    cur, conn = setupdb("Covid_Temp_Animals.db")

    #make the database table
    makedb(cur, conn)
    
    #add 25 each to database
    storedb(cur, conn, databaseDict)

    # #get data to plot visualization 1
    data1 = get_graph_data(cur, conn)

    #write dictionary as txt
    create_file("Daily_Temp_Difference_vs_Cases.txt", data1)
   
    # plot visualization 1
    visualization1(data1)

    #get data to plot visualization 2
    data2 = get_graph2_data(cur, conn)

    #write dictionary as txt
    create_file("Seasonal_Temp_vs_Cases.txt", data2)
    
    #plot visualization 2
    visualization2(data2)

    
    
