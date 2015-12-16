#-*- encoding:utf-8 -*-
import sys,os
import logging
from logging.handlers import RotatingFileHandler

#__currentPath__ = os.path.dirname(sys.executable)
def getLogger():
    if os.path.basename(sys.executable) == "python.exe":
        __currentPath__ = os.getcwd()
    else:
        __currentPath__ = os.path.dirname(sys.executable)
    __logLevel__ = logging.NOTSET #WARNING
    __logFile__ = os.path.join(__currentPath__,'Service.log')
    __formatter__ = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'

    logHandler = RotatingFileHandler(__logFile__, maxBytes=4*1024,backupCount=5)
    logHandler.setLevel(__logLevel__)
    logHandler.setFormatter(logging.Formatter(__formatter__));

    Logger = logging.getLogger()
    Logger.setLevel(__logLevel__)
    Logger.addHandler(logHandler)
    return Logger
