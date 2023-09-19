#### 使用说明
工单平台：
1.启动采集器
***** 一次请只启动一个，不然任务会混乱，后面改名改redis库编号再解决
celery -A src.services.mweibo_worker.app worker -l info -P gevent -c 60
celery -A src.services.weixin.app worker -l info -P gevent -c 60
celery -A src.services.douyin_worker.app worker -l info -P gevent -c 60
celery -A src.services.redbook_worker.app worker -l info -P gevent -c 60
celery -A src.services.bili_worker.app worker -l info -P gevent -c 60

2.启动kafka 存储器
kafka_consumer.py   

修改kafka_executor() 参数为平台名


3.发送任务
send_task()  参数为平台名
'start_ts': 1500000000,
'end_ts': 1650000000,
配置一下开始结束时间

