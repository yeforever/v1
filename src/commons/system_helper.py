#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@version: 1.0
@author: guu
@contact: yeexiao@yeah.net
@time: 19/7/2018 10:56 AM
"""

from src.config.main import system_config


class SystemHelper(object):

    @classmethod
    def is_prod_env(cls):
        """ 当前是否是生产环境

        :return:
        """
        return True if system_config['env'] == 'prod' else False

    @classmethod
    def is_debug_mode(cls):
        return system_config['debug']
