#!/home3/lafontai/python/Python-2.7.2/python
# -*- coding: UTF-8 -*-
from __future__ import division
print "Content-Type: text/plain; charset=utf-8"
print 

import cgi
import cgitb

cgitb.enable(display=1,logdir="/home3/lafontai/public_html/logs/pythonlog.txt")

import datetime as dt
import numpy as np
import scipy as sp
from numpy.fft import *
import calendar
from scipy import signal
from sklearn.cluster import DBSCAN
import itertools




def transformCalendar(startDate,endDate,fuzzyness,cycle,cycleFreq):
    if cycle == 1:
        dateList = [startDate + dt.timedelta(days=x*cycleFreq) for x in range(0, 1+np.floor((endDate-startDate).days/cycleFreq).astype('int'))]
    elif cycle == 2:
        dateList = [dt.datetime(startDate.year+int((startDate.month+x*cycleFreq-1)//12), int((startDate.month+x*cycleFreq-1)%12+1), min(startDate.day,(calendar.monthrange(startDate.year+int((startDate.month+x*cycleFreq-1)//12),int((startDate.month+x*cycleFreq-1)%12+1)))[1])) for x in range(0, 1+np.floor(round((endDate-startDate).days/30)/cycleFreq).astype('int'))]
    elif cycle == 3:
        dateList = [dt.datetime(startDate.year+int(x*cycleFreq), startDate.month, startDate.day) for x in range(0, 1+np.floor(round((endDate-startDate).days/365)/cycleFreq).astype('int'))]
    return dateList


def add2Calendar(startDate,endDate,fuzzyness,cycle,cycleFreq):
    if cycle == 1:
        dateList = [startDate + dt.timedelta(days=x*cycleFreq) for x in range(0, 2+np.floor((endDate-startDate).days/cycleFreq).astype('int'))]
    elif cycle == 2:
        dateList = [dt.datetime(startDate.year+int((startDate.month+x*cycleFreq-1)//12), int((startDate.month+x*cycleFreq-1)%12+1), min(startDate.day,calendar.monthrange(startDate.year+int((startDate.month+x*cycleFreq-1)//12),int((startDate.month+x*cycleFreq-1)%12+1))[1] )) for x in range(0, 2+np.floor(round((endDate-startDate).days/30)/cycleFreq).astype('int'))]
    elif cycle == 3:
        dateList = [dt.datetime(startDate.year+int(x*cycleFreq), startDate.month, startDate.day) for x in range(0, 2+np.floor(round((endDate-startDate).days/365)/cycleFreq).astype('int'))]
    return dateList[-1]



def patternScore2(realCalendar,startDate,endDate,fuzzyness,cycle,cycleFreq):
    w = 1 # Penalty for missing a prediction
    if cycle==1 and cycleFreq-fuzzyness <= 2:   #Periods cannot overlap
        return 0
    noCycles = np.floor(SubDate(startDate,endDate)[cycle]/cycleFreq).astype('int')
    hitDays = 1+noCycles*(1+2*fuzzyness) #Total days there might be events including fuzzyness
    totalDays = (endDate-startDate).days
    precision = cycle*cycle/fuzzyness
    patternCalendar = transformCalendar(startDate,endDate,fuzzyness,cycle,cycleFreq)
    predictions = [(np.min(np.abs((date-realCalendar)))).days<=fuzzyness for date in patternCalendar]
    trueMfalse = (1+w)*np.sum(predictions)-w*len(predictions) -1 # True positives - False positives - 1
    # because the first one is meaningless
    return (precision*trueMfalse)



def SubDate(date1, date2):
    differences = [0 ,
                      (date2-date1).days,
                      date2.month - date1.month + (date2.year-date1.year)*12,
                      date2.year-date1.year]
    return differences



def calendar2Signal(calendar):
    signals = np.zeros((max(calendar)-min(calendar)).days+1)
    for date in calendar:
        signals[(date-min(calendar)).days] = 1
    return signals



def findPeriod_Fourier(realCalendar):
    signal=calendar2Signal(realCalendar)
    Transform = np.fft.rfft(signal)
    n = len(signal)
    
    peakind = sp.signal.find_peaks_cwt(np.square(np.real(Transform)), np.arange(1,10))
    Periods = np.unique(np.round((1/np.fft.rfftfreq(n,1))[peakind]))
    #print Periods
    
    #plt.plot(1/np.fft.rfftfreq(n,1), np.square(np.real(Transform)))
    
    return Periods
    #return plotScatter(1/np.fft.rfftfreq(n,1), np.square(np.real(Transform)))

def findPeriod_Differences(realCalendar):
	DateCombinations = list(itertools.combinations(realCalendar,2))
	return np.unique(np.abs([(a-b).days for a,b in DateCombinations]))

def monthDivider(curDate, iniDate, period):
    MonthDiff = curDate.month - iniDate.month + (curDate.year-iniDate.year)*12
    monthMod = MonthDiff%period
    monthPer = np.floor(MonthDiff/period)
    Mod = min(curDate.day, 28) + 28*monthMod    #We may want to deal with February better

    return [Mod/(28*period*2), monthPer/12]



def yearDivider(curDate, iniDate, period):
    yearDiff = curDate.year-iniDate.year
    yearMod = yearDiff%period
    yearPer = np.floor(yearDiff/period)
    Mod = curDate.timetuple().tm_yday + 365*yearMod

    return [Mod/(365*period*2), yearPer/12]



def findPattern(realCalendar):
    # Function to step through time making predictions but blind to the future
    # Algorithm will always make a prediction based on a pattern score
    # Function will return all predictions made, the score that made it and if it was correct   
    endDate = realCalendar[-1]
    BestScore = 0
    BestSet = (None,None,None,None,None,None)
    if len(realCalendar)>10:
    	Periods = findPeriod_Fourier(realCalendar)
    else:
    	Periods = findPeriod_Differences(realCalendar)
    
    #Always try a yearly cycle, fourier isn't good at checking this with the given parameters
    #changing parameters will just slow it down so it's not worth it (from observation)
    CycleFreq = 1
    X = np.array([yearDivider(date, realCalendar[0], CycleFreq) for date in realCalendar])
    xShift = np.zeros(X.shape)
    xShift[:,0] = .5
    X = np.vstack((X,X+xShift))
    #X = StandardScaler().fit_transform(X) # I'm normalizing in yearDivider
    DB = DBSCAN(eps=.4, min_samples=1).fit(X)
    #return X,CycleFreq,DB
    mainLabel = (sp.stats.mode(DB.labels_))[0]
    realCalendar2 = np.hstack((realCalendar, realCalendar))
    startDate = np.min(realCalendar2[DB.labels_==mainLabel]) 
    # Find fuzziness. A perfect pattern is currently not allowed/ min(fuzziness) = 1
    mods = X[DB.labels_==mainLabel,0]
    cyclePos = X[DB.labels_==mainLabel,1]
    meanMod = np.mean(mods)
    modDiff = np.abs(mods-meanMod)
    trimMods = []
    #Correct for two dates in same cycle
    for pos in np.unique(cyclePos):
        trimMods.append((mods[cyclePos==pos])[np.argmin(modDiff[cyclePos==pos])])
    meanMod = np.mean(trimMods)
    # Start date should be at the mean modulus
    startDate = startDate+dt.timedelta(days=365*CycleFreq*2*(meanMod-(yearDivider(startDate, realCalendar[0], CycleFreq))[0]))
    fuzziness = max(np.ceil((np.max(trimMods) - np.min(trimMods))*365*CycleFreq*2/2),1)
    
    if fuzziness<180:   #Limit on fuzziness is half a year
        Score = patternScore2(realCalendar,startDate, endDate,fuzziness,3,max(CycleFreq,1))
        if Score>BestScore:
            BestScore = Score
            BestSet = (BestScore,startDate, endDate,fuzziness,3,CycleFreq) 
    
    if np.any(Periods):
        for Period in Periods:   
            if Period>20:    # If relevant cycle through months
                CycleFreq = round(Period/30)
                X = np.array([monthDivider(date, realCalendar[0], CycleFreq) for date in realCalendar])
                xShift = np.zeros(X.shape)
                xShift[:,0] = .5
                X = np.vstack((X,X+xShift))
                #X = StandardScaler().fit_transform(X) # I'm normalizing in monthDivider
                DB = DBSCAN(eps=.1, min_samples=1).fit(X)
                mainLabel = (sp.stats.mode(DB.labels_))[0]
                realCalendar2 = np.hstack((realCalendar, realCalendar))
                startDate = np.min(realCalendar2[DB.labels_==mainLabel]) 
                # Find fuzziness. A perfect pattern is currently not allowed/ min(fuzziness) = 1
                mods = X[DB.labels_==mainLabel,0]
                cyclePos = X[DB.labels_==mainLabel,1]
                u, indices,counts = np.unique(cyclePos, return_index=True, return_counts=True)
                if np.min(counts)==2:
                	counts = counts/2
                	
                #print 'Labels='
                #print DB.labels_
                #print 'Indices ='
                #print indices
                #print 'Counts ='
                #print counts
                #print 'Period ='
                #print Period
                meanMod = np.mean(mods[indices[counts==1]])
                modDiff = np.abs(mods-meanMod)
                trimMods = []
                #Correct for two dates in same cycle
                for pos in np.unique(cyclePos):
                    trimMods.append((mods[cyclePos==pos])[np.argmin(modDiff[cyclePos==pos])])
                meanMod = (np.max(trimMods)+np.min(trimMods))/2
                # Start date should be at the mean modulus
                startDate = startDate+dt.timedelta(days=28*CycleFreq*2*(meanMod-(monthDivider(startDate, realCalendar[0], CycleFreq))[0]))
                fuzziness = max(np.ceil((np.max(trimMods) - np.min(trimMods))*28*CycleFreq*2/2),1)

                if fuzziness<Period:
                    Score = patternScore2(realCalendar,startDate, endDate,fuzziness,2,max(CycleFreq,1))
                    if Score>BestScore:
                        BestScore = Score
                        BestSet = (BestScore,startDate, endDate,fuzziness,2,CycleFreq) 
            
            #Always cycle through days (for a given period)
            DateDiffs = [(date-realCalendar[0]).days for date in realCalendar]
            Mods = np.array(DateDiffs%Period)
            Mods = np.hstack((Mods,Period+Mods))
            Floors = np.array(np.floor(DateDiffs/Period))
            Floors = np.hstack((Floors,Floors))
            X = (np.vstack((Mods,Floors))).T
            X[:,0] = X[:,0]/(2*Period)
            X[:,1] = X[:,1]/24    # At the day scale every cycle becomes less significant? 24>12
            #X = StandardScaler().fit_transform(X)
            DB = DBSCAN(eps=.2, min_samples=1).fit(X)
            #return X, Period, DB
            mainLabel = (sp.stats.mode(DB.labels_))[0]
            realCalendar2 = np.hstack((realCalendar, realCalendar))
            startDate = np.min(realCalendar2[DB.labels_==mainLabel]) 
            # Find fuzziness. A perfect pattern is currently not allowed/ min(fuzziness) = 1
            mods = X[DB.labels_==mainLabel,0]
            cyclePos = X[DB.labels_==mainLabel,1]
            meanMod = np.mean(mods)
            modDiff = np.abs(mods-meanMod)
            trimMods = []
            #Correct for two dates in same cycle
            for pos in np.unique(cyclePos):
                trimMods.append((mods[cyclePos==pos])[np.argmin(modDiff[cyclePos==pos])])
            meanMod = np.median(trimMods)

            # Start date should be at the mean modulus
            startDate = startDate+dt.timedelta(days=(Period*2*meanMod-(startDate-realCalendar[0]).days%Period))
            fuzziness = max(np.ceil((np.max(trimMods) - np.min(trimMods))*Period*2/2),1)

            if fuzziness<Period:
                Score = patternScore2(realCalendar,startDate, endDate,fuzziness,1,max(Period,1))
                if Score>BestScore:
                    BestScore = Score
                    BestSet = (BestScore,startDate, endDate,fuzziness,1,Period)  
	
    return BestSet
            
    
postData = cgi.FieldStorage()

textCalendar=np.array(postData.getvalue("realCalendar").split(','))
realCalendar=np.array(sorted([dt.datetime.strptime(date,'%Y-%m-%d') for date in textCalendar]))

#json_data=open("/media/Libraries/Documents/Insight/Data/user0.json").read()
#userData = json.loads(json_data)
#flightData = pd.DataFrame([Datum['data'] for Datum in userData])
#flightData['end_dt'] = pd.to_datetime(flightData['end_dt'])
#flightData['start_dt'] = pd.to_datetime(flightData['start_dt'])
#realCalendar = np.array(sorted(flightData[flightData.end_airport=='SNA'].start_dt))

BestSet = findPattern(realCalendar)
if BestSet[0]:
	nextDate = add2Calendar(*BestSet[1:])
else:
	nextDate = BestSet[0]

print BestSet[0]
print nextDate.strftime('%Y-%m-%d')
print BestSet[1].strftime('%Y-%m-%d')
print BestSet[3]
print BestSet[4]
print BestSet[5]


