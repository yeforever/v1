pip3 install /app/docker/boost-py-0.1.0.tar.gz
pip3 install -r /app/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com
python3 init.py
celery -A src.services.worker.mweibo_worker.app worker -l info -P gevent -c 60