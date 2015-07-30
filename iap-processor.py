import collections
import pandas as pd
import math

iapData = pd.read_csv('dd2-iap-query.csv')

# Clean the data - remove blank s rows.
iapData = iapData[pd.notnull(iapData['s'])]

# create a wrapper function to generate rounding functions.
def roundup(x):
    def rounderFunc(num):
        return int(math.ceil(num / float(x))) * x
    return rounderFunc

# create round up to 100 function.  Will take a num and round up to 100.
# Will be used to take in IAP v and roundup to nearest 100; 
# will get more useful dollar ranges than going w/ 0.99 values.
# later will divide by 100 to get dollars.
roundUp100 = roundup(100)


# Create spender bucket distro.
spendRangeArr = [
    0,
    4.9, 
    5,
    10,
    20, 
    30,
    50,
    75, 
    100,
    150,
    200,
    300,
    400,
    500,
    750,
    1000,
    1500,
    2000,
    3000,
    5000,
    5000.01,
]

spenderRangeDict = spendRangeDictBuilder(spendRangeArr)

# Automatically creates dic based on spender bucket array
# Will use this to pivot based on buckets.
def spendRangeDictBuilder(spendArr):
    dictOutput = {}

    idx = 0
    for num in spendArr:
        if idx == len(spendArr) - 1:
            dictOutput[num] = str(num) + "+"
        elif idx != 0:
            dictOutput[num] = str(spendArr[idx-1] + 0.01) + " - " + str(num)
        else:
            dictOutput[num] = "0"
        
        idx += 1
    
    return dictOutput


# Binary search function to return lowest num from Arr that is 
# greater than the input num.
# if the num is greater than the entire list, returns the last num.

def binaryLowestGreater(array, iMin, iMax, num):
    mid = math.floor((iMin + iMax) / 2)

    if iMin == iMax:
        return array[iMin]

    if array[mid] < num:
        return binaryLowestGreater(array, mid + 1, iMax, num)
    elif array[mid] == num:
        return array[mid]
    else:
        return binaryLowestGreater(array, iMin, mid -1, num)