import os
import datetime

DEBUG = True


def get_the_time():
        dateTimeObj = datetime.datetime.now()
        timestampStr = dateTimeObj.strftime("%d%b%Y_%H%M%S%f")
        return timestampStr

def init_globals():
        global filename
        global progress
        progress = 0
        filename = ''