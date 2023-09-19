#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@version: 1.0
@author: guu
@contact: yeexiao@yeah.net
@time: 7/8/17 9:24 PM
"""

from boost_py.databases import mysql

from src.commons.system_helper import SystemHelper
from src.config import main
from src.config import main_local


class DatabaseHelper(object):
    """
        数据库连接helper类: 获取mysql连接
    """

    @classmethod
    def get_erp_db(cls):
        if SystemHelper.is_prod_env():
            return 'qmg_erp_prod'
        else:
            return 'qmg_erp_dev'

    @classmethod
    def get_dts_db(cls):
        if SystemHelper.is_prod_env():
            return 'dts_prod'
        else:
            return 'dts_dev'

    @classmethod
    def get_mysql_db(cls, database: str):
        """ 获得指定mysql数据库的连接配置

        :param database:
        :return:
        """
        if hasattr(main_local, 'mysql_config') \
                and database in main_local.mysql_config:
            config = main_local.mysql_config[database]
        elif hasattr(main, 'mysql_config') \
                and database in main.mysql_config:
            config = main.mysql_config[database]
        else:
            raise Exception('mysql database:[%s] not configured' % database)

        return mysql.get_pooled_db(database, **config)

    # @classmethod
    # def get_mysql_conn_url(cls, database: str):
    #     """ 获得指定mysql数据库的连接url
    #
    #     :param database: 数据库名称
    #     :return:
    #     """
    #     if database in local_mysql_config:
    #         config = local_mysql_config[database]
    #     elif database in mysql_config:
    #         config = mysql_config[database]
    #     else:
    #         raise Exception('mysql database:[%s] not configured in main config file.' % database)
    #     db_url = 'mysql+pymysql://{user}:{password}@{ip}:{port}/{db}'.format(user=config['user'],
    #                                                                          password=config['password'],
    #                                                                          ip=config['host'],
    #                                                                          port=config['port'],
    #                                                                          db=database)
    #     return db_url
