#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@version: 1.0
@author: guu
@contact: yeexiao@yeah.net
@time: 7/8/17 9:24 PM
"""

import logging
from logging.handlers import RotatingFileHandler

from src.config.main import system_config
from src.commons.system_helper import SystemHelper


class LoggingHelper(object):

    loggers = {
        'dev': {

        },
        'prod': {

        }
    }

    @classmethod
    def get_logger(cls, app_name: str):
        fm = logging.Formatter('%(asctime)s %(filename)s line:%(lineno)d [%(levelname)s] %(message)s')
        logger = logging.getLogger(app_name)

        fh = RotatingFileHandler(system_config['logs_path'] + '/%s.log' % app_name,
                                 encoding='utf-8',
                                 maxBytes=1024*1024*5,
                                 backupCount=2)
        fh.setFormatter(fm)
        logger.addHandler(fh)
        logger.setLevel(logging.DEBUG if system_config['debug'] else logging.INFO)

        if SystemHelper.is_prod_env():
            if app_name in cls.loggers['prod']:
                return cls.loggers['prod'][app_name]
            else:
                cls.loggers['prod'][app_name] = logger
                return logger
        else:
            if app_name in cls.loggers['dev']:
                return cls.loggers['dev'][app_name]
            else:
                sh = logging.StreamHandler()
                sh.setFormatter(fm)
                logger.addHandler(sh)

                cls.loggers['dev'][app_name] = logger
                return logger

    @classmethod
    def is_debug_mode(cls):
        return system_config['debug']
