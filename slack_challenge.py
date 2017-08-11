import re
import datetime as dt
from functools import total_ordering
from collections import defaultdict

@total_ordering
class Numeric(object):
    def __init__(self, value):
        self.payload = value

    def __lt__(self, rhs):

        if isinstance(rhs, Date):
            return True
        elif isinstance(rhs, str):
            return True
        return float(self.payload) < float(rhs.payload)

    def __eq__(self, rhs):
        if not isinstance(rhs, Numeric):
            return False
        return self.payload == rhs.payload

    def __str__(self):
        return self.payload

    def __repr__(self):
        return "Numeric: " + self.payload


@total_ordering
class Date(object):
    def __init__(self, value):
        self.payload = value
        year, month, day = re.split(r'\/|\-', value)
        self.__date = dt.date(int(year), int(month), int(day))

    def __str__(self):
        return self.payload

    def __lt__(self, rhs):
        if not isinstance(rhs, Date):
            return False
        return self.__date < rhs.__date

    def __eq__(self, rhs):
        if not isinstance(rhs, Date):
            return False
        return self.__date == rhs.__date

    def __repr__(self):
        return "Date: " + self.payload

def containsDate(string):
    return re.search('\d{4}[\/\-]\d{2}[\/\-]\d{2}', string)

def processList(xs):
    result = []
    for x in xs:
        if x is not [] and isinstance(x, list):
            for y in x:
                result.append(y)
        else:
            result.append(x)
    return result

def sanitize(string):
    if not isinstance(string, str):
        return string
    else:
        return string.lower()

def canCastToInt(string):
    try:
        int(string)
        return True
    except:
        return False

def isNumeric(string):
    numeric_pattern = '[\-\.]?\d+(\.\d*)?'
    return re.fullmatch(numeric_pattern, string)

def findDates(string):
    date_pattern =  '(\d{4}[- \/.]\d{2}[- \/.]\d{2})'
    return re.split(date_pattern, string)

def findDelimiters(string):
    delimiter_pattern = '([\ \-\/\.])'
    if isinstance(string, (Date, Numeric)):
        return string
    else:
        return re.split(delimiter_pattern, string)

def findNumeric(string):
    numeric_pattern = '[\-\.]?\d+(\.\d*)?'
    return re.fullmatch(numeric_pattern, string)

def processDates(string):
    date_pattern =  '(\d{4}[- \/.]\d{2}[- \/.]\d{2})'
    if re.fullmatch(date_pattern, string):
        return Date(string)
    return string

def processAlphaNumeric(string):
    split_pattern = '(\d+)'
    if not isinstance(string, str):
        return string
    else:
        return re.split(split_pattern, string)


def data_key(string):
    if isNumeric(string):
        return [Numeric(string)]
    else:
        result = findDates(string)
        result = list(map(processDates, result))
        result = list(map(findDelimiters, result))
        result = processList(result)
        result = list(map(processAlphaNumeric, result))
        result = processList(result)
        result = [Numeric(x) if canCastToInt(x) else x for x in result]
        result =  [sanitize(s) for s in result]
        return result

def type_signatures(collection):
    return str([type(element) for element in data_key(collection)])

def sortStrings(strings):

    result_dictionary = defaultdict(list)

    for string in strings:
        result_dictionary[type_signatures(string)].append(string)
    
    result = []
    for _, value in result_dictionary.items():
        value.sort(key=data_key)
        result = result + value

    return result