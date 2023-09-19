"""
@version: 1.0
@author: anne
@contact: thy.self@foxmail.com
@time: 2021/11/27 上午11:16
"""
import sys
import _thread
import json

from kafka import KafkaConsumer
from loguru import logger
from peewee import fn

from src.commons.common_job_params import platform_code_save, platform_code_en, platform_code_query


def kafka_consumer_executor(platform):
    """

    :param platform:
    :return:
    """
    topic_name = platform_code_en[platform]
    consumer = KafkaConsumer(topic_name, bootstrap_servers=["106.15.138.230:9092"])
    logger.info(f'当前启动topic消费者：{topic_name}')

    pl = platform_code_query[platform]
    max_id = pl.select(fn.MAX(pl.id).alias('max_id'))[0].max_id
    max_id = max_id if max_id else 1
    logger.info(f'当前已消费的最大id：{str(max_id)}')

    for msg in consumer:
        info = json.loads(str(msg.value, encoding='utf8'))
        logger.info(info)
        max_id += 1
        # 异步insert 数据到mysql, 工单数据单句存储，异步提高速度
        _thread.start_new_thread(platform_code_save[platform], (info, max_id))


if __name__ == '__main__':
    # python3 -m src.services.kafka.kafka_consumer 1
    kafka_consumer_executor(int(sys.argv[1]))
