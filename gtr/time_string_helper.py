import re

def parse_time(timestring):
    minutes_list = re.findall(r"((\d+)m)", timestring)
    hours_list = re.findall(r"((\d+)h)", timestring)
    minutes = 0

    if len(minutes_list) > 0:
        minutes += int(minutes_list[0][1])
    if len(hours_list):
        minutes += int(hours_list[0][1]) * 60

    if timestring.startswith('added'):
        return minutes
    elif timestring.startswith('subtracted'):
        return -minutes
    else:
        return 0