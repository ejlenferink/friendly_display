from machine import RTC
import time

class Departure:
    
    def __init__(self, route, destination, when, stop_name=""):
        self.route = route
        self.destination = destination
        self.when = when
        self.stop_name = stop_name
        
    @property
    def minutes_away(self):
        now = time.time()
        
        date_part, time_part = self.when.split('T')
        
        year = int(date_part[0:4])
        month = int(date_part[5:7])
        day = int(date_part[8:10])

        hour = int(time_part[0:2])
        minute = int(time_part[3:5])
        second = int(time_part[6:8])

        offset_sign = time_part[8]
        offset_hours = int(time_part[9:11])
        offset_minutes = int(time_part[12:14])

        offset_seconds = (offset_hours * 3600) + (offset_minutes * 60)

        time_tuple = (year, month, day, hour, minute, second, 0, 0)
        local_epoch = time.mktime(time_tuple)

        if offset_sign == '-':
            utc_epoch = local_epoch + offset_seconds
        else:
            utc_epoch = local_epoch - offset_seconds

        seconds_away = utc_epoch - now
        return max(0, int(seconds_away // 60))

        