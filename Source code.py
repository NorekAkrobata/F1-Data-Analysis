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

#Creating df/lists for graphs

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

#Constructors - Points difference at the end of the season

#williams = constructors_points_year[constructors_points_year["name"] == "Williams"] 

groupedWilliams = constructors_points_year[constructors_points_year["name"] == "Williams"].groupby('year').points.sum()
rest = constructors_points_year[constructors_points_year["name"] != "Williams"]
rest = (rest.groupby(['year', 'name']).agg({'points':'sum'})).groupby('year').points.max() #To calculate difference - Others

pointsdiff = pd.merge(groupedWilliams, rest, on='year') #Merging both df's
pointsdiff['difference'] = pointsdiff.points_x - pointsdiff.points_y #Creating points difference columns

list1 = [1980, 1981, 1986, 1987, 1992, 1993, 1994, 1996, 1997] #List of years when Williams won constructor Championships - for scatter plot
williamsScatter = pointsdiff[pointsdiff.index.isin(list1)]

#rest = constructors_points_year[constructors_points_year["name"] != "Williams"]
#williams2 = williams[williams["year"].isin(list1)]
#groupedwilliams = williams.groupby("year").points.sum() #To calculate difference - Williams
#groupedwilliams2 = williams2.groupby("year").points.sum() #To prepare scatter plot
#rest1 = (rest.groupby(['year', 'name']).agg({'points':'sum'})).groupby('year').points.max() #To calculate difference - Others

#Plot preparation - Points difference

plt.plot(pointsdiff.index, pointsdiff.difference, label='Points difference')
plt.scatter(williamsScatter.index, williamsScatter.difference, color='r', marker='d', label='World Championship')
plt.ylabel('Points difference')
plt.xlabel('Year')
plt.legend(loc='best')
plt.title('Williamss points advantage over the best of the rest')
plt.savefig('PointsDifference1977-2019.png', dpi=300,bbox_inches='tight')
plt.show()

######################

#Drivers - Points
drivers = csvs[4]
drivers["fullname"] = drivers["forename"] + " " + drivers["surname"]
drivers = drivers[["driverId", "fullname"]]

driverspoints = csvs[5]
driverspoints = driverspoints[["raceId", "driverId", "points", "wins"]]

drivers_points0 = pd.merge(drivers, driverspoints, on="driverId")
drivers_points = pd.merge(drivers_points0, races, on="raceId")
aggre = {"points":"max", "wins":"max"}
drivers_points_grouped = drivers_points.groupby(["fullname", "year"]).agg(aggre).reset_index()
grouped_points = drivers_points_grouped.groupby("fullname").points.sum().sort_values(ascending=False)
grouped_points = grouped_points[0:10]
grouped_wins = drivers_points_grouped.groupby("fullname").wins.sum().sort_values(ascending=False)
grouped_wins = grouped_wins[0:10]

#Laptimes - Constructors

l1 = csvs[10][['raceId', 'driverId', 'constructorId', 'laps', 'milliseconds']]
l2 = csvs[9][['raceId', 'year', 'name']]
l3 = csvs[1][['constructorId', 'name']]
l3.rename(columns = {'name':'cname'}, inplace=True) #rename column to distinguish it from gp name
ll1 = pd.merge(l1, l2, on='raceId')
laptimes = pd.merge(ll1, l3, on='constructorId')

laptimes.milliseconds = pd.to_numeric(laptimes.milliseconds, errors='coerce') #converting milliseconds to numeric while /N is converted to NaN
laptimes = laptimes[laptimes.milliseconds.notna()]
laptimes['averagetime'] = laptimes.milliseconds/laptimes.laps/1000
laptimes = laptimes[laptimes.year >= 1977]
laptimes = laptimes[['raceId', 'year', 'name', 'cname', 'averagetime']]
laptimesWilliams = laptimes[laptimes.cname == 'Williams']
laptimesWilliams1 = laptimesWilliams.groupby('raceId').agg({'year':'first', 'name':"first", 'averagetime':"min"})
laptimesRest = laptimes[laptimes.cname != 'Williams']
laptimesRest1 = laptimesRest.groupby('raceId').agg({'year':'first', 'name':'first', 'averagetime':'min'})
laptimesRest2 = laptimesRest1[laptimesRest1.index.isin(laptimesWilliams1.index)]

proposal = pd.merge(laptimesWilliams1, laptimesRest2, on="raceId")
proposal = proposal[['year_x', 'name_x', 'averagetime_x', 'averagetime_y']]
proposal['difference'] = proposal.averagetime_x - proposal.averagetime_y
proposal1 = proposal.groupby('year_x', as_index=False).agg({'difference':'mean'})
list1 = [1980, 1981, 1986, 1987, 1992, 1993, 1994, 1996, 1997]
proposal2 = proposal1[proposal1.year_x.isin(list1)]

#Best laptimes - Constructors
k1 = csvs[10][['raceId', 'driverId', 'constructorId', 'fastestLapTime', 'fastestLapSpeed']]
k2 = csvs[9][['raceId', 'year', 'name']]
k3 = csvs[1][['constructorId', 'name']]

k1['fastestLapSpeed'] = pd.to_numeric(k1.fastestLapSpeed, errors='coerce')
k1 = k1[k1['fastestLapTime'] != '\\N']

def convert(y):
    m1,s1 = [float(x) for x in y.split(':')]
    laptime = m1*60 + s1
    return laptime

k1['fastestLapTimeSEC'] = k1['fastestLapTime'].apply(convert)


k3.rename(columns = {'name':'cname'}, inplace=True) #rename column to distinguish it from gp name
kk1 = pd.merge(k1, k2, on='raceId')
laptimesBEST = pd.merge(kk1, k3, on='constructorId')
laptimesBEST = laptimesBEST[['raceId', 'fastestLapSpeed', 'fastestLapTimeSEC', 'year', 'name', 'cname']]
laptimesBESTWilliams = laptimesBEST[laptimesBEST.cname == 'Williams']
laptimesBESTWilliams1 = laptimesBESTWilliams.groupby('raceId').agg({'year':'first', 'name':'first', 'fastestLapSpeed':'max'})
laptimesBESTWilliams2 = laptimesBESTWilliams.groupby('raceId').agg({'year':'first', 'name':'first', 'fastestLapTimeSEC':'min'})
laptimesBESTRest = laptimesBEST[laptimesBEST.cname != 'Williams']
laptimesBESTRest1 = laptimesBESTRest.groupby('raceId').agg({'year':'first', 'name':'first', 'fastestLapSpeed':'max'})
laptimesBESTRest2 = laptimesBESTRest.groupby('raceId').agg({'year':'first', 'name':'first', 'fastestLapTimeSEC':'min'})
laptimesBESTRest1 = laptimesBESTRest1[laptimesBESTRest1.index.isin(laptimesBESTWilliams1.index)]
laptimesBESTRest2 = laptimesBESTRest2[laptimesBESTRest2.index.isin(laptimesBESTWilliams2.index)]

proposal3=pd.merge(laptimesBESTWilliams1, laptimesBESTRest1, on='raceId')
proposal3=proposal3[['year_x', 'name_x', 'fastestLapSpeed_x', 'fastestLapSpeed_y']]
proposal3['difference'] = proposal3.fastestLapSpeed_x - proposal3.fastestLapSpeed_y
proposal3 = proposal3[proposal3.difference > -13.5]
proposal33 = proposal3.groupby('year_x', as_index=False).agg({'difference':'mean'})
proposal4=pd.merge(laptimesBESTWilliams2, laptimesBESTRest2, on='raceId')
proposal4=proposal4[['year_x', 'name_x', 'fastestLapTimeSEC_x', 'fastestLapTimeSEC_y']]
proposal4['difference'] = proposal4.fastestLapTimeSEC_x - proposal4.fastestLapTimeSEC_y
proposal44 = proposal4.groupby('year_x', as_index=False).agg({'difference':'mean'})

list1 = [1980, 1981, 1986, 1987, 1992, 1993, 1994, 1996, 1997]
proposal333 = proposal1[proposal1.year_x.isin(list1)]

year2019speed = proposal3[proposal3['year_x']==2019]
year2019speed = year2019speed.groupby(['year_x', 'name_x'], as_index=False).agg({'difference':'first'})
year2019speed['name_x'] = year2019speed.name_x.str.replace('Grand Prix', 'GP')

year2019lap = proposal4[proposal4['year_x']==2019]
year2019lap = year2019lap.groupby(['year_x', 'name_x'], as_index=False).agg({'difference':'first'})
year2019lap['name_x'] = year2019lap.name_x.str.replace('Grand Prix', 'GP')

#Highest speed 2004-2019 - plot11

proposal34 = proposal3.groupby(['year_x', 'name_x'], as_index=False).agg({'difference':'first'})

plt.figure(1)
plt.scatter(proposal34.index, proposal34.difference, c=proposal34.difference, s=5)
z = np.polyfit(proposal34.index, proposal34.difference, 1)
p = np.poly1d(z)
plt.plot(proposal34.index,p(proposal34.index),"r--")
plt.show()

#Highest speed 2019 - plot9

plt.plot(year2019speed.name_x, year2019speed.difference)
plt.ylabel('Km/h')
plt.xlabel('Grand Prix')
plt.title('Różnica w prędkosci maksymalnej w 2019 - Williams, a najlepszy z pozostałych')
plt.xticks(rotation=90)
plt.savefig('SpeedDifference2019.png', dpi=300,bbox_inches='tight')
plt.show()

#Best laptime 2019 - plot10

plt.plot(year2019lap.name_x, year2019lap.difference)
plt.ylabel('s')
plt.xlabel('Grand Prix')
plt.title('Różnica w najszybszym okrążeniu w 2019 - Williams, a najlepszy z pozostałych')
plt.xticks(rotation=90)
plt.savefig('PaceDifference2019.png', dpi=300,bbox_inches='tight')
plt.show()

#Laptimes - plot5

plt.plot(proposal1.year_x, proposal1.difference, label='Róznica')
plt.scatter(proposal2.year_x, proposal2.difference, color='r', marker='d', label='Mistrzostwa')
plt.ylabel('Sekundy/okrążenie')
plt.xlabel('Rok')
plt.legend(loc='best')
plt.title('Różnica w tempie wyscigowym - Williams, a najlepszy z pozostałych')
plt.savefig('PaceDifference1977-2019.png', dpi=300,bbox_inches='tight')
plt.show()

#Highest speed - plot6

plt.plot(proposal33.year_x, proposal33.difference)
z = np.polyfit(proposal33.year_x, proposal33.difference, 1)
p = np.poly1d(z)
plt.plot(proposal33.year_x,p(proposal33.year_x),"r--")
plt.ylabel('Km/h')
plt.xlabel('Rok')
plt.title('Różnica w prędkosci maksymalnej - Williams, a najlepszy z pozostałych')
plt.savefig('SpeedDifference2004-2019.png', dpi=300,bbox_inches='tight')
plt.show()

#Best laptimes - plot 7
plt.plot(proposal44.year_x, proposal44.difference)
z = np.polyfit(proposal44.year_x, proposal44.difference, 1)
p = np.poly1d(z)
plt.plot(proposal44.year_x,p(proposal44.year_x),"r--")
plt.ylabel('s')
plt.xlabel('Rok')
plt.title('Różnica w najszybszym okrążeniu - Williams, a najlepszy z pozostałych')
plt.savefig('BestLapDifference2004-2019.png', dpi=300,bbox_inches='tight')
plt.show()

#Points difference - plot8

plt.plot(pointsdiff.index, pointsdiff.difference, label='Różnica punktowa')
plt.scatter(williams3.index, williams3.difference, color='r', marker='d', label='Mistrzostwa')
plt.ylabel('Różnica punktów')
plt.xlabel('Rok')
plt.legend(loc='best')
plt.title('Przewaga punktowa Williamsa nad najlepszym z pozostałych')
plt.savefig('PointsDifference1977-2019.png', dpi=300,bbox_inches='tight')
plt.show()

#Plot2
groupedwilliams.plot(kind="line", label = "Punkty")
groupedwilliams2.plot(style="d", label = "Mistrzostwa konstruktorów")
plt.ylabel("Liczba punktów")
plt.xlabel("Rok")
plt.xticks(rotation=45)
plt.title("Punkty zdobyte przez zespół Williams w latach 1977-2019")
#[plt.axvline(x=j, color = "red", label="Mistrzostwo konstruktorow") for j in x]
#axvlines(x)
plt.legend(loc="best")
plt.savefig("williams.png", dpi=300, bbox_inches='tight')
plt.show()

#Plot3
colors=['b']*10
for i in (4,6,7,8,9):
    colors[i]='r'
punkty = grouped_points.plot(kind="bar", width=0.75, color=colors)
plt.ylabel("Liczba punktów")
plt.xlabel("Kierowca")
plt.xticks(rotation=60)
plt.title("Najlepsza 10 - Punkty zdobyte przez kierowców w latach 1977-2019")
for p in punkty.patches:
    punkty.annotate(str(int(p.get_height())), (p.get_x(), p.get_height() * 1.01))
plt.savefig("DriversPoints.png", dpi=300,bbox_inches='tight')
plt.show()

#Plot4
colors=['b']*10
for i in (3,4,6):
    colors[i]='r'
wins = grouped_wins.plot(kind="bar", color=colors)
plt.ylabel("Liczba zwycięstw")
plt.xlabel("Kierowca")
plt.xticks(rotation=60)
plt.title("Najlepsza 10 - Zwycięstwa odniesione przez kierowców")
for p in wins.patches:
    wins.annotate(str(int(p.get_height())), (p.get_x() +.05, p.get_height() * 1.01))
plt.savefig("DriversWins.png", dpi=300,bbox_inches='tight')
plt.show()


#Plotting multiple vertical lines as 1 object
def axvlines(xs, ax=None, **plot_kwargs):
    """
    Draw vertical lines on plot
    :param xs: A scalar, list, or 1D array of horizontal offsets
    :param ax: The axis (or none to use gca)
    :param plot_kwargs: Keyword arguments to be passed to plot
    :return: The plot object corresponding to the lines.
    """
    if ax is None:
        ax = plt.gca()
    xs = np.array((xs, ) if np.isscalar(xs) else xs, copy=False)
    lims = ax.get_ylim()
    x_points = np.repeat(xs[:, None], repeats=3, axis=1).flatten()
    y_points = np.repeat(np.array(lims + (np.nan, ))[None, :], repeats=len(xs), axis=0).flatten()
    plot = ax.plot(x_points, y_points, scaley = False, **plot_kwargs)
    return plot



