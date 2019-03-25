# coding: utf-8

import logging


#日志系统， 日志输出到控制台并写入日志文件
class Logger():

    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, level_s=DEBUG, level_f=WARNING, filename=None, name=None):

        # 创建一个logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.NOTSET)

        # 定义handler的输出格式
        formatter_s = logging.Formatter(
            fmt='[%(levelname)s] %(asctime)s %(name)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
        formatter_f = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] - %(name)s - [%(lineno)d]: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

        # 创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(level_s)
        ch.setFormatter(formatter_s)

        self.logger.addHandler(ch)

        if filename:
            # 创建一个handler，用于写入日志文件
            fh = logging.FileHandler(filename, encoding='utf-8')
            fh.setLevel(level_f)
            fh.setFormatter(formatter_f)
            self.logger.addHandler(fh)

    def getlogger(self):
        return self.logger
