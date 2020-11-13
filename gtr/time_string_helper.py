import re
import datetime
from dateutil.parser import parse

def parse_time(timestring):
    minutes_list = re.findall(r"((\d+)m)", timestring)
    hours_list = re.findall(r"((\d+)h)", timestring)
    hours = 0

    if len(minutes_list) > 0:
        hours += int(minutes_list[0][1]) / 60
    if len(hours_list):
        hours += int(hours_list[0][1])

    if timestring.startswith('added'):
        return hours
    elif timestring.startswith('subtracted'):
        return -hours
    else:
        return 0

def parse_week(datestring):
    date = parse(datestring).date() - datetime.timedelta(days=1)
    return date.isocalendar()[1]