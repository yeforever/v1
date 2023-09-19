docker run --name brief_mweibo_worker -d dts-auto-brief-v1:prod celery -A src.services.worker.mweibo_worker.app worker -l info -P gevent -c 60
docker run --name brief_weixin_worker -d dts-auto-brief-v1:prod celery -A src.services.worker.weixin_worker.app worker -l info -P gevent -c 60
docker run --name brief_redbook_worker -d dts-auto-brief-v1:prod celery -A src.services.worker.redbook_worker.app worker -l info -P gevent -c 60
docker run --name brief_douyin_worker -d dts-auto-brief-v1:prod celery -A src.services.worker.douyin_worker.app worker -l info -P gevent -c 60
docker run --name brief_bili_worker -d dts-auto-brief-v1:prod celery -A src.services.worker.bili_worker.app worker -l info -P gevent -c 60
docker run --name brief_kafka_weibo_consumer -d dts-auto-brief-v1:prod python3 -m src.services.kafka_consumer 1
docker run --name brief_kafka_weixin_consumer -d dts-auto-brief-v1:prod python3 -m src.services.kafka_consumer 2
docker run --name brief_kafka_redbook_consumer -d dts-auto-brief-v1:prod python3 -m src.services.kafka_consumer 3
docker run --name brief_kafka_douyin_consumer -d dts-auto-brief-v1:prod python3 -m src.services.kafka_consumer 4
docker run --name brief_kafka_bili_consumer -d dts-auto-brief-v1:prod python3 -m src.services.kafka_consumer 5
docker run --name brief_job_manager -d -p 8999:8999 dts-auto-brief-v1:prod python3 -m src.applications.job_manager