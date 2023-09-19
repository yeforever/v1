"""
@version: 1.0
@author: anne
@contact: thy.self@foxmail.com
@time: 2021/11/4 上午11:51
"""
import json
import uuid

from src.services.worker.mweibo_worker import app as mweibo_worker
from src.services.worker.douyin_worker import app as douyin_worker
from src.services.worker.weixin_worker import app as weixin_worker
from src.services.worker.redbook_worker import app as redbook_worker
from src.services.worker.bili_worker import app as bili_worker


def send_task(tt):
    # tt = 'weibo'
    if tt == 'weibo':
        app = mweibo_worker
    elif tt == 'weixin':
        app = weixin_worker
    elif tt == 'douyin':
        app = douyin_worker
    elif tt == 'redbook':
        app = redbook_worker
    elif tt == 'bili':
        app = bili_worker
    else:
        return None
    task_uuid = str(uuid.uuid4())
    for i in range(1, 2):
        task = {
                'task_uuid': task_uuid,
                'stage_uuid': 'a',
                'start_ts': 1500000000,
                'end_ts': 1650000000,
                'keyword': '口红',
                'page': i
            }
        app.send_task(f'{tt}.{tt}', [task])


if __name__ == '__main__':
    send_task('weibo')
