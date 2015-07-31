import collections
import pandas as pd
import math
from datetime import datetime
import numpy as np

# Clean the data - remove blank s rows.
# sort by server time.
def dataProcess(data):
    data = data[pd.notnull(data['s'])]
    data.sort('server_time', inplace=True)
    return data

# create a wrapper function to generate rounding functions.
def roundup(x):
    def rounderFunc(num):
        return int(math.ceil(num / float(x))) * x
    return rounderFunc

# create round up to 100 function.  Will take a num and round up to 100.
# Will be used to take in IAP v and roundup to nearest 100; 
# will get more useful dollar ranges than going w/ 0.99 values.
# later will divide by 100 to get dollars.

# Create spender bucket distro.

# Automatically creates dic based on spender bucket array
# Will use this to pivot based on buckets.
def spendRangeDictBuilder(spendArr):
    dictOutput = {}

    idx = 0
    for num in spendArr:
        if idx == len(spendArr) - 1:
            dictOutput[num] = str(num) + "+"
        elif idx != 0:
            dictOutput[num] = str(spendArr[idx-1] + 1) + " - " + str(num)
        else:
            dictOutput[num] = "0"
        
        idx += 1
    
    return dictOutput


# Binary search function to return lowest num from Arr that is 
# greater than the input num.
# if the num is greater than the entire list, returns the last num.
# I'll be using this to match the player's calculated IAP with their spending group.

def binaryLowestGreater(array, iMin, iMax, num):
    print(iMin, iMax, num)

    mid = int(math.floor((iMin + iMax) / 2))

    print(mid, array[mid])
    print(iMin, iMax, num)

    if iMin == iMax:
        return array[iMin]

    if array[mid] < num:
        return binaryLowestGreater(array, mid + 1, iMax, num)
    elif array[mid] == num:
        return array[mid]
    else:
        return binaryLowestGreater(array, iMin, mid, num)

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return ((d2 - d1).days)

def columnAdderAgg(data, colNameDict):
    data = roundColumn(data,colNameDict['iapRounded'])
    data = daysAgedColumn(data,colNameDict['daysAged'])
    data = sumAndCountCols(data, 
                           data['s'],
                           data['iapRounded'],
                           colNameDict['iapSumRunningTotal'],
                           colNameDict['iapSumTotal'],
                           colNameDict['iapCountRunningTotal'],
                           colNameDict['iapCountTotal'])

    return data

def sDictToArr(dict, sArr):
    def sMapFunc(sID):
        return dict[sID]

    outputArr = map(sMapFunc, sArr)

    return outputArr


# This one is a bit sloppy.  Built on side effects (but at least all internal to the function)
# And it changes 4 at a time.  But it seems more efficient than breaking them up just for the
# sake of breaking them up.  Don't know.  Moving on, but may reconsider at some point.
def sumAndCountCols(data, sCol, iapRoundedCol, sumRunName, sumTotName, ctRunName, ctTotName):

    iapSumDict = collections.defaultdict(int)
    iapSumRunList = []
    iapCtDict = collections.defaultdict(int)
    iapCtRunList = []

    def sumRedFunc(accum, curr):
        accum[curr[0]] += curr[1]

        #side effects ftw! >__>
        iapSumRunList.append(accum[curr[0]])
        iapCtDict[curr[0]] += 1
        iapCtRunList.append(iapCtDict[curr[0]])
        return accum

    nameIAPTupList = zip(sCol,iapRoundedCol)

    iapSumDict = reduce(sumRedFunc,nameIAPTupList,iapSumDict)

    iapSumTotalList = sDictToArr(iapSumDict, data['s'])
    iapCtTotalList = sDictToArr(iapCtDict, data['s'])

    iapSumRunArr = np.asarray(iapSumRunList)
    iapSumTotArr = np.asarray(iapSumTotalList)
    iapCtRunArr = np.asarray(iapCtRunList)
    iapCtTotArr = np.asarray(iapCtTotalList)

    data[sumRunName] = iapSumRunArr
    data[sumTotName] = iapSumTotArr
    data[ctRunName] = iapCtRunArr
    data[ctTotName] = iapCtTotArr

    return data

def roundColumn(data, colName):
    def vModMapFunc(x):
        return roundUp100(x)/100

    data[colName] = data['v'].map(vModMapFunc)
    return data

def daysAgedColumn(data, colName):
    dateTupList = zip(data['install_date'], data['server_date'])

    def dateMapFunc(x):
        return days_between(x[0], x[-1])

    data[colName] = map(dateMapFunc, dateTupList)
    return data

spendRangeArr = [
    0,
    4,
    9,
    19,
    29, 
    49,
    74,
    99, 
    124,
    149,
    199,
    299,
    399,
    499,
    749,
    999,
    1499,
    1999,
    2999,
    4999,
    5000
]

# Master dict for naming the new columns.  Just change the value to change actual output.
# No need to make major changes to the script.
colNameDict = {
    'iapRounded': 'iapRounded',
    'daysAged': 'daysAged',
    'iapSumRunningTotal': 'iapSum',
    'iapSumTotal': 'iapTotal',
    'iapCountRunningTotal': 'iapCt',
    'iapCountTotal': 'iapCtTotal'
}

roundUp100 = roundup(100)

iapData = pd.read_csv('dd2-iap-query.csv')

# might just wrap this into the column aggregator.  Process the data, then add columns.
# don't really need to run this separately.
iapDataClean = dataProcess(iapData)

spenderRangeDict = spendRangeDictBuilder(spendRangeArr)

iapDataNewCols = columnAdderAgg(iapDataClean, colNameDict)

print iapDataNewCols

