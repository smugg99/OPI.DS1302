#!/usr/bin/env python3

# write RPi current date and time (UTC time) to DS1302 RTC chip
# read value after write to check update

import datetime
import sys
from OPI_DS1302 import DS1302

rtc = DS1302(clk_pin=7, data_pin=5, ce_pin=8)

try:
    # write date and time from system to RTC chip (in UTC)
    dt_write = datetime.datetime.utcnow()
    # update rtc
    rtc.write_datetime(dt_write)
    # check update is good
    dt_read = rtc.read_datetime()
    if -2 < (dt_write - dt_read).total_seconds() < +2:
        print(dt_write.strftime('%Y-%m-%dT%H:%M:%SZ'))
    else:
        exit('unable to set RTC time')
except ValueError:
    sys.exit('error with RTC chip, check wiring')
finally:
    rtc.close()
