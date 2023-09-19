"""
@version: 1.0
@author: anne
@contact: thy.self@foxmail.com
@time: 2021/11/29 上午11:44
"""
from kafka import KafkaConsumer, KafkaProducer

producer = KafkaProducer(bootstrap_servers="106.15.138.230:9092")
# weibo_consumer = KafkaConsumer('weibo', bootstrap_servers=["106.15.138.230:9092"])
# weixin_consumer = KafkaConsumer('weixin', bootstrap_servers=["106.15.138.230:9092"])
# douyin_consumer = KafkaConsumer('douyin', bootstrap_servers=["106.15.138.230:9092"])
# redbook_consumer = KafkaConsumer('redbook', bootstrap_servers=["106.15.138.230:9092"])
# bili_consumer = KafkaConsumer('bili', bootstrap_servers=["106.15.138.230:9092"])