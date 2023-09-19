"""
@version: 1.0
@author: anne
@contact: thy.self@foxmail.com
@time: 2021/11/4 下午5:04
"""
import time


class DateTimeHelper(object):
    @classmethod
    def is_timestamp(cls, val):
        try:
            int(val)
            return True
        except ValueError:
            return False

    @classmethod
    def parse_formatted_datetime(cls, formatted_time: str, fmt: str):
        return int(time.mktime(time.strptime(formatted_time, fmt)))

    @classmethod
    def format_datetime(cls, timestamp, fmt='%Y-%m-%d %H:%M:%S'):
        if cls.is_timestamp(timestamp):
            return time.strftime(fmt, time.localtime(int(timestamp)))
        else:
            raise ValueError('%s is not timestamp.' % timestamp)
