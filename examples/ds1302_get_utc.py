#!/usr/bin/env python3

# read date and time from RTC chip, return ISO 8601 UTC string
# assume DS1302 contain UTC time and not local

import sys
import OPI_DS1302 as pyRPiRTC

rtc = pyRPiRTC.DS1302(clk_pin=7, data_pin=5, ce_pin=8)

try:
    # read date and time from RTC chip
    dt = rtc.read_datetime()
    print(dt.strftime('%Y-%m-%dT%H:%M:%SZ'))
except ValueError:
    sys.exit('error with RTC chip, check wiring')
finally:
    # clean close
    rtc.close()
