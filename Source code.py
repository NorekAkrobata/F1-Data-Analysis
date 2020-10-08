# -*- coding: utf-8 -*-

#Libraries
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn

seaborn.set()
pd.set_option("display.max_columns", None)

#Importing files
path = "C:\\Users\\Norbert\\Desktop\\f1db_csv"
os.chdir(path) #change current working dir
os.getcwd() #current working dir
fileslist_csv = [f for f in glob.glob("*.csv")] #csv files list
csvs = [pd.read_csv(i) for i in fileslist_csv] #Read all csv files

#Description for files list
#0 - cirtuits
#1 - constructors
#2 - constructor results
#3 - constructor results2
#4 - drivers
#5 - drivers results
#6 - lap results
#7 - pitstops
#8 - quali
#9 - GP's
#10 - GP results
#11 - nothing important
#12 - status

#Constructors - Points
constructors = csvs[1][["constructorId", "name"]]
points = csvs[2][["constructorId", "points", "raceId"]]
races = csvs[9][["raceId", "year"]]

constructors_points = pd.merge(constructors, points, on="constructorId")
constructors_points_year = pd.merge(constructors_points, races, on="raceId")
constructors_points_year = constructors_points_year[constructors_points_year["year"] >= 1978] #Filtering to only match years when Williams was present in F1

ConstructorsPoints = constructors_points_year.groupby("name").points.sum().sort_values(ascending=False)[0:10] #Top 10 - Constructors with most points 1977-2019

#Plot preparation - ConstructorPoints
colors=['b']*10
colors[4]='r'
ConstructorsPoints.plot(kind="bar", color=colors)
plt.ylabel("Points")
plt.xlabel("Constructors")
plt.xticks(rotation=45)
plt.title("Top 10 - Points gained by constructors between 1977-2019")
plt.savefig("ConstructorsPoints.png", dpi=300,bbox_inches='tight')
plt.show()

#Constructors - Points difference at the end of each season

groupedWilliams = constructors_points_year[constructors_points_year["name"] == "Williams"].groupby('year').points.sum()
rest = constructors_points_year[constructors_points_year["name"] != "Williams"]
rest = (rest.groupby(['year', 'name']).agg({'points':'sum'})).groupby('year').points.max() #To calculate difference - Others

pointsdiff = pd.merge(groupedWilliams, rest, on='year') #Merging both df's
pointsdiff['difference'] = pointsdiff.points_x - pointsdiff.points_y #Creating points difference columns

list1 = [1980, 1981, 1986, 1987, 1992, 1993, 1994, 1996, 1997] #List of years when Williams won constructor Championships - for scatter plot
williamsScatter = pointsdiff[pointsdiff.index.isin(list1)]

#Plot preparation - Points difference

plt.plot(pointsdiff.index, pointsdiff.difference, label='Points difference')
plt.scatter(williamsScatter.index, williamsScatter.difference, color='r', marker='d', label='World Championship')
plt.ylabel('Points difference')
plt.xlabel('Year')
plt.legend(loc='best')
plt.title('Williamss points advantage over the best of the rest')
plt.savefig('PointsDifference1977-2019.png', dpi=300,bbox_inches='tight')
plt.show()

#Constructors - Race pace difference each year 

gpResults = csvs[10][['raceId', 'driverId', 'constructorId', 'laps', 'milliseconds']]
racesResults = csvs[9][['raceId', 'year', 'name']]
constructorResults = csvs[1][['constructorId', 'name']]
constructorResults.rename(columns = {'name':'cname'}, inplace=True) #rename column to distinguish it from gpResults name

temp1 = pd.merge(gpResults, racesResults, on='raceId')
lapTimes = pd.merge(temp1, constructorResults, on='constructorId')

lapTimes.milliseconds = pd.to_numeric(lapTimes.milliseconds, errors='coerce') #converting milliseconds to numeric while /N is converted to NaN
lapTimes = lapTimes[lapTimes.milliseconds.notna()] #Filtering for rows without NaN's
lapTimes = lapTimes[lapTimes.year >= 1977] #Filtering for years when Williams was present in F1
lapTimes['averagetime'] = lapTimes.milliseconds/lapTimes.laps/1000  #Calculating average time per lap
lapTimes = lapTimes[['raceId', 'year', 'name', 'cname', 'averagetime']] #Taking just necessary columns

lapTimesWilliams = lapTimes[lapTimes.cname == 'Williams'].groupby('raceId').agg({'year':'first', 'name':"first", 'averagetime':"min"}) #Creating summary for Williams
lapTimesRest = lapTimes[lapTimes.cname != 'Williams'].groupby('raceId').agg({'year':'first', 'name':'first', 'averagetime':'min'}) #Creating summary for rest of the teams
lapTimesRest = lapTimesRest[lapTimesRest.index.isin(lapTimesWilliams.index)] #Making sure that both df's will contain same amount of data

lapTimesDifference = pd.merge(lapTimesWilliams, lapTimesRest, on="raceId")
lapTimesDifference = lapTimesDifference[['year_x', 'name_x', 'averagetime_x', 'averagetime_y']]
lapTimesDifference['difference'] = lapTimesDifference.averagetime_x - lapTimesDifference.averagetime_y #Creating difference column
lapTimesDifference = lapTimesDifference.groupby('year_x', as_index=False).agg({'difference':'mean'})
lapTimesScatter = lapTimesDifference[lapTimesDifference.year_x.isin(list1)] #For scatter plot to show when Williams won championships

#Plot preparation - Race pace difference each year

plt.plot(lapTimesDifference.year_x, lapTimesDifference.difference, label='Difference')
plt.scatter(lapTimesScatter.year_x, lapTimesScatter.difference, color='r', marker='d', label='Championships')
plt.ylabel('Seconds per lap')
plt.xlabel('Year')
plt.legend(loc='best')
plt.title('Difference in race pace - Williams vs best of the rest')
plt.savefig('PaceDifference1977-2019.png', dpi=300,bbox_inches='tight')
plt.show()

#Constructors - Best lap and highest speed difference

gpResults1 = csvs[10][['raceId', 'driverId', 'constructorId', 'fastestLapTime', 'fastestLapSpeed']]
racesResults1 = csvs[9][['raceId', 'year', 'name']]
constructorResults1 = csvs[1][['constructorId', 'name']]
constructorResults1.rename(columns = {'name':'cname'}, inplace=True) #rename column to distinguish it from gp name

gpResults1['fastestLapSpeed'] = pd.to_numeric(gpResults1.fastestLapSpeed, errors='coerce') #Convert to numeric
gpResults1 = gpResults1[gpResults1['fastestLapTime'] != '\\N'] #Filter rows without NaN's

def convert(y):
    #Function to convert time into desired format - seconds
    m1,s1 = [float(x) for x in y.split(':')]
    laptime = m1*60 + s1
    return laptime

gpResults1['fastestLapTimeSEC'] = gpResults1['fastestLapTime'].apply(convert) #Apply function over whole column

temp2 = pd.merge(gpResults1, racesResults1, on='raceId')
temp3 = pd.merge(temp2, constructorResults1, on='constructorId')
lapBest = temp3[['raceId', 'fastestLapSpeed', 'fastestLapTimeSEC', 'year', 'name', 'cname']] #Taking only necessary columns

lapBestWilliams = lapBest[lapBest.cname == 'Williams']
WilliamsTopSpeed = lapBestWilliams.groupby('raceId').agg({'year':'first', 'name':'first', 'fastestLapSpeed':'max'})
WilliamsBestLap = lapBestWilliams.groupby('raceId').agg({'year':'first', 'name':'first', 'fastestLapTimeSEC':'min'})

lapBestRest = lapBest[lapBest.cname != 'Williams']
RestTopSpeed = lapBestRest.groupby('raceId').agg({'year':'first', 'name':'first', 'fastestLapSpeed':'max'})
RestBestLap = lapBestRest.groupby('raceId').agg({'year':'first', 'name':'first', 'fastestLapTimeSEC':'min'})

RestTopSpeed = RestTopSpeed[RestTopSpeed.index.isin(WilliamsTopSpeed.index)] #Ensuring right comparison
RestBestLap = RestBestLap[RestBestLap.index.isin(WilliamsBestLap.index)]

TopSpeed=pd.merge(WilliamsTopSpeed, RestTopSpeed, on='raceId')
TopSpeed=TopSpeed[['year_x', 'name_x', 'fastestLapSpeed_x', 'fastestLapSpeed_y']]
TopSpeed['difference'] = TopSpeed.fastestLapSpeed_x - TopSpeed.fastestLapSpeed_y
TopSpeed = TopSpeed[TopSpeed.difference > -13.5]
TopSpeedFinal = TopSpeed.groupby('year_x', as_index=False).agg({'difference':'mean'})

BestLap=pd.merge(WilliamsBestLap, RestBestLap, on='raceId')
BestLap=BestLap[['year_x', 'name_x', 'fastestLapTimeSEC_x', 'fastestLapTimeSEC_y']]
BestLap['difference'] = BestLap.fastestLapTimeSEC_x - BestLap.fastestLapTimeSEC_y
BestLapFinal=BestLap.groupby('year_x', as_index=False).agg({'difference':'mean'})

#Plots preparation - Best lap and highest speed difference

plt.plot(TopSpeedFinal.year_x, TopSpeedFinal.difference)
z = np.polyfit(TopSpeedFinal.year_x, TopSpeedFinal.difference, 1)
p = np.poly1d(z)
plt.plot(TopSpeedFinal.year_x,p(TopSpeedFinal.year_x),"r--")
plt.ylabel('Km/h')
plt.xlabel('Year')
plt.title('Top speed difference - Williams vs best of the rest')
plt.savefig('SpeedDifference2004-2019.png', dpi=300,bbox_inches='tight')
plt.show()

plt.plot(BestLapFinal.year_x, BestLapFinal.difference)
z = np.polyfit(BestLapFinal.year_x, BestLapFinal.difference, 1)
p = np.poly1d(z)
plt.plot(BestLapFinal.year_x,p(BestLapFinal.year_x),"r--")
plt.ylabel('Seconds')
plt.xlabel('Year')
plt.title('Best laptime difference - Williams vs best of the rest')
plt.savefig('BestLapDifference2004-2019.png', dpi=300,bbox_inches='tight')
plt.show()