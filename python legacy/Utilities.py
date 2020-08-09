from datetime import datetime, date


def formatNumber(numbers):
    value = '('
    for acode in numbers[0:3]:
        value += str(acode)
    value += ') '
    for f3 in numbers[3:6]:
        value += str(f3)
    value += '-'
    for l4 in numbers[6:11]:
        value += l4
    return value


def indexOfLastDigit(number):
    index = 0
    for x in range(0, len(number)):
        if (number[x].isdigit()):
            index = x
    return index


def parseDateTime(fileName):
    for i in [i for i, ltr in enumerate(fileName) if ltr == '_']:
        fileName = fileName[:i] + ':' + fileName[i + 1:]
    try:
        return datetime.fromisoformat(fileName[fileName.rindex(' ') + 1:fileName.rindex('Z')])
    except ValueError as err:
        try:
            return date.fromisoformat(fileName[fileName.rindex(' ') + 1:fileName.rindex('T')])
        except Exception as err2:
            raise Exception


def sortDictionaryByDate(history):
    return sorted(history)
