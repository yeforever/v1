#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@version: 1.0
@author: adair
@contact: adair.ma@amdigital.cn
@time: 2020/2/5:10:31
"""

import requests
import traceback

from src.config.services import DTS_ALARM_SYSTEM


class AlarmHelper(object):
    """
    告警通知接口
    """

    @classmethod
    def send_wechat(cls, msg, user, log_url, err_title, err_service, remark):
        user_config = {
            '张晔': 'oWSAr0dbeuMYPVF8_A-yBigKLZRQ',
            '马理想': 'oWSAr0c4InTggSVjLhnIpSeP7tTo',
            '陶宏杨': 'oWSAr0YgNmgNRhH5MvR5C3g5AvPs',
            '王小飞': 'oWSAr0ZMeaq6lFyC7o_H4ASK6TCM'
        }
        params = {"openid": user_config[user],
                  "log_url": log_url,
                  "err_title": err_title,
                  "err_host": "0.0.0.0",
                  "err_service": err_service,
                  "err_status": "error",
                  "err_msg": msg,
                  "remark": remark
                  }
        try:
            resp = requests.post(url=DTS_ALARM_SYSTEM['send_wechat'], data=params)
            print(resp.text)
            return False
        except Exception:
            return True

    @classmethod
    def send_work_wechat(cls, msg, view_url, err_title, err_service):
        import socket
        # 获取本机电脑名
        myname = socket.getfqdn(socket.gethostname())
        # 获取本机ip
        myaddr = socket.gethostbyname(myname)
        # todo 新建linux 内网外网映射，告警提示外网ip

        params = {
            "log_url": view_url,
            "err_title": err_title,
            "err_host": myaddr,
            "err_service": err_service,
            "err_status": "ok",
            "err_msg": msg
        }
        try:
            resp = requests.post(url=DTS_ALARM_SYSTEM['send_work_wechat'], data=params)

            print(resp.text)
            return False
        except Exception:
            return True

    @classmethod
    def send_email(cls):
        user_config = {
            '张晔': '',
            '马理想': '',
            '陶宏杨': '125806935@qq.com',
            '王小飞': ''
        }
        params = {"email_title": "憨憨改代码了", "email_text": "今晚删你代码", "receiver_name": "憨憨",
                  "receiver_email": user_config['陶宏杨']
                  }
        try:
            resp = requests.post(url=DTS_ALARM_SYSTEM['end_email'], data=params)
            print(resp.text)
            return False
        except Exception:
            return True

    @classmethod
    def send_51wom_submit(cls, created_name, code, created_time, delay_num, status, end_time):

        params = {
            "created_name": created_name,
            "code": code,
            "created_time": created_time,
            "delay_num": delay_num,
            "status": status,
            "end_time": end_time
        }
        try:
            resp = requests.post(url=DTS_ALARM_SYSTEM['send_51wom_submit'], data=params)

            print(resp.text)
            return False
        except Exception:
            return True

    @classmethod
    def send_51wom_finish(cls, created_name):
        params = {
            "created_name": created_name
        }
        try:
            resp = requests.post(url=DTS_ALARM_SYSTEM['send_51wom_finish'], data=params)

            print(resp.text)
            return False
        except Exception:
            return True


if __name__ == '__main__':
    AlarmHelper.send_work_wechat('cookie即将过期', 'https://baidu.com', '微信cookie过期', '微信cookie过期')
