#!/usr/bin/python

# https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/master/Adafruit_CharLCD

from LCD import LCD
from subprocess import * 
from time import sleep, strftime
from datetime import datetime

lcd = LCD()

cmd = "ip addr show wlan0 | grep inet | awk '{print $2}' | cut -d/ -f1"

lcd.begin(16,1)

def run_cmd(cmd):
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()[0]
        return output.split('\n')[0]

while 1:
    lcd.clear()
    ipaddr = run_cmd(cmd)
    lcd.message(datetime.now().strftime('%b %d  %H:%M:%S\n'))
    lcd.message('IP %s' % ( ipaddr ) )
    sleep(1)
