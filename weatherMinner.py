import requests as r
import csv
import json
import argparse
from multiprocessing import Pool

def writeCsv(data, csvfilename):
    #write data to csv
    csvfile = open(csvfilename, "w+")
    fieldnames = ["date", "max", "min", "average", "departure", "hdd", "cdd", "precipitation", "newsnow", "snowdepth"]
    csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #Write label header
    csvwriter.writerow(dict(zip(fieldnames, fieldnames)))
    for i in data:
        csvwriter.writerow(i)

def extractToDict(data):
    #Convert the json data to a DictWriter friendly version 
    endList = []
    templateDict = {"date": "", "max": "", "min": "", "average": "", "departure": "", "hdd": "", "cdd": "", "precipitation": "", "newsnow": "", "snowdepth": ""}
    keyIndex = list(templateDict.keys())
    for entries in data["data"]:
        templateDict = {"date": "", "max": "", "min": "", "average": "", "departure": "", "hdd": "", "cdd": "", "precipitation": "", "newsnow": "", "snowdepth": ""}
        for i in range(0,len(entries)):
            if type(entries[i]) == list:
                templateDict[keyIndex[i]] = entries[i][0]
            else:
                templateDict[keyIndex[i]] = entries[i]

        endList.append(templateDict)
    return endList

def extractTempData(station, sdate, edate):
    #Makes a call to rcc-acis api endpoint
    #Requesting one months worth of data in this case
    #This is somewhat documented on http://www.rcc-acis.org/docs_webservices.html
    #The "undocumented" part is the station lists, but you can find that
    #by scraping https://w2.weather.gov/climate/xmacis.php
    #Sdata and Edate must be in Year-Month-Date format
    #Local var defs
    endpoint = "https://data.rcc-acis.org/StnData"
    jsonData = '{"params":{"elems":[{"name":"maxt","add":"t"},{"name":"mint","add":"t"},{"name":"avgt","add":"t"},{"name":"avgt","normal":"departure","add":"t"},{"name":"hdd","add":"t"},{"name":"cdd","add":"t"},{"name":"pcpn","add":"t"},{"name":"snow","add":"t"},{"name":"snwd","add":"t"}],"sid":"CHANGE","sDate":"PLACEHOLDER","eDate":"PLACEHOLDER"}, "output": "json"}'
    #Json modification
    desJson = json.loads(jsonData)
    desJson["params"]["sid"] = station
    desJson["params"]["sDate"] = sdate
    desJson["params"]["eDate"] = edate
    jsonData = json.dumps(desJson)
    #Make the request
    result = r.post(endpoint, data=jsonData, headers={"content-type":"application/json"})
    data = extractToDict(result.json())
    fileName = (station.replace(" ", "-")) + ".csv"
    writeCsv(data, fileName)

def buildPoolList(sdate, edate):
    #builds the list of tuples for starmap() 
    #to allow for multiprocessing
    #List should be [(stationName, sdate, edate), ...]
    with open("station_list.txt", "r") as stationData:
        data = json.loads(stationData.read())
        retList = []
        for i in data:
            tmpTup = (i[0] + " " + i[2], sdate, edate)
            retList.append(tmpTup)

        return retList


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", type=str, help="The date to start from, format is year-month-day")
    parser.add_argument("-e", "--end", type=str, help="The date to stop at format is year-month-day")
    args = parser.parse_args()
    if args.start and args.end:
        run = buildPoolList(args.start, args.end)
        with Pool(5) as pool:
            pool.starmap(extractTempData, run)
    else:
        print("Need arguments")
        exit()

if __name__ == "__main__":
    main()
