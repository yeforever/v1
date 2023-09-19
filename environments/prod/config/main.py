#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__all__ = ['system_config', 'mysql_config', 'mongodb_config', 'redis_config']

# config for system
system_config = {
    'name': '{name}',
    'path': '{path}',
    'runtime_path': '{path}/runtime',
    'logs_path': '{path}/runtime/logs',
    'time_zone': 'Asia/Shanghai',
    'env': 'prod',
    'debug': True
}

# config settings for mysql
mysql_config = {
    'dts_prod': {
        'host': 'rm-m5ex13f9qkq9s0w0aso.mysql.rds.aliyuncs.com',
        'port': 3306,
        'user': 'dts_prod_admin',
        'password': 'MxZIVHD0iIG^Yxv2',
        'charset': 'utf8mb4'
    },
    'dts_dev': {
        'host': 'rm-m5ex13f9qkq9s0w0aso.mysql.rds.aliyuncs.com',
        'port': 3306,
        'user': 'dts_prod_admin',
        'password': 'i7ny34d87snu7162$',
        'charset': 'utf8mb4'
    }
}

# config settings for mongodb
mongodb_config = {
    'wom-dts-datawarehouse': {
        'host': 'dds-m5e296a1c97603741182-pub.mongodb.rds.aliyuncs.com',
        'port': 3717,
        'user': 'dts-datawarehouse-admin',
        'password': 'aowB0y6yQyPOc9h'
    }
}
# config setting for redis
redis_config = {
    'host': 'r-m5e9fb82ca98ce34pd.redis.rds.aliyuncs.com',
    'port': 6379,
    'password': 'Womi2020'
}
