# !/usr/bin/python
# -*-coding:utf-8-*-
# filename:myLogger.py

import logging
import logging.handlers
import os

class Logger:
    needPrint = False
    logger = logging.getLogger("usercenter")
    logger.setLevel(logging.DEBUG)
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/logs/')

    rh = logging.handlers.TimedRotatingFileHandler('{0}log.txt'.format(path), when='D', backupCount=7)
    fm = logging.Formatter('[%(asctime)s] %(filename)s-[line:%(lineno)d] %(levelname)s--%(message)s', '%Y-%m-%d %H:%M:%S')
    rh.setFormatter(fm)
    logger.addHandler(rh)

    @staticmethod
    def need_print(need_print):
        Logger.needPrint = need_print
        return

    @staticmethod
    def debug(txt):
        Logger.logger.debug(txt)
        if Logger.needPrint:
            print txt

    @staticmethod
    def warning(txt):
        Logger.logger.warning(txt)
        if Logger.needPrint:
            print txt

    @staticmethod
    def info(txt):
        Logger.logger.info(txt)
        if Logger.needPrint:
            print txt

    @staticmethod
    def error(txt):
        Logger.logger.error(txt)
        if Logger.needPrint:
            print txt

    @staticmethod
    def critical(txt):
        Logger.logger.critical(txt)
        if Logger.needPrint:
            print txt
if __name__ == '__main__':
    # Logger.needprint(True)
    Logger.debug('1')
    Logger.debug('2')
    Logger.debug('3')
    Logger.critical("test")
