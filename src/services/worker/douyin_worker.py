"""
@version: 1.0
@author: yezi
@contact: yezi.self@foxmail.com
@time: 2021/11/4 下午5:03
"""
import json

import requests
from celery import Celery

from src.commons.datatime_helper import DateTimeHelper
from src.commons.exception_helper import merry_except
from src.commons.whosecard_open_platform import WhosecardDySpider
from src.config.main import redis_config
from src.commons.kafka_helper import producer

"""
用户详情
https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid=MS4wLjABAAAA6lwGsdvKaZe5PJVHH9ocMI_PMkfyVx9poNHWndDH7p4
https://www.douyin.com/aweme/v1/user/profile/other/?sec_user_id=MS4wLjABAAAA6lwGsdvKaZe5PJVHH9ocMI_PMkfyVx9poNHWndDH7p4&iid=4&device_id=3

文章详情
https://www.douyin.com/web/api/v2/aweme/iteminfo/?item_ids=7024839582453697805
https://www.douyin.com/aweme/v1/aweme/detail/?aweme_id=7024839582453697805
"""


class SpiderDouyin(object):
    """
    抖音平台采集
    """

    HEADERS = {
        'authority': 'www.iesdouyin.com',
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.61 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'zh-CN,zh;q=0.9'
    }

    @classmethod
    @merry_except
    def spider_list(cls, keyword, page):
        cursor = 12 * (page - 1)
        result = WhosecardDySpider.get_search(keyword=keyword, cursor=cursor, search_source='video_search',
                                              sort_type=0,
                                              publish_time=0)
        if not result:
            return {}
        if not result.get('ok'):
            return {}
        if result.get("ok"):
            return_data = result['result']
            return {
                'aweme_list': return_data['aweme_list'],
                'has_more': return_data['has_more'],
                'cursor': return_data['cursor']
            }

    @classmethod
    @merry_except
    def spider_user(cls, sec_uid, info: dict):
        response = requests.get(f'https://www.iesdouyin.com/web/api/v2/user/info?sec_uid={sec_uid}',
                                headers=cls.HEADERS).json()
        info['user_like_num'] = int(response['user_info']['total_favorited'])  # 用户总点赞数
        info['user_fans_num'] = response['user_info']['follower_count']  # 用户总粉丝数
        info['user_attention_num'] = response['user_info']['following_count']  # 用户总关注数
        info['douyin_id'] = response['user_info']['short_id']  # 抖音id
        return info


app = Celery(
    'douyin',
    backend=f'redis://:{redis_config["password"]}@{redis_config["host"]}:{redis_config["port"]}/16',
    broker=f'redis://:{redis_config["password"]}@{redis_config["host"]}:{redis_config["port"]}/17'
)


#  celery -A src.services.worker.douyin_worker.app worker -l info -P gevent -c 60
@app.task(name="douyin.douyin")
def crawler_douyin(task):
    su = SpiderDouyin.spider_list(task.get('keyword'), task.get('page'))
    if su:
        for i in su.get('aweme_list'):
            if task.get('start_ts') <= i['create_time'] <= task.get('end_ts'):
                info = {'title': i['share_info']['share_title'], 'content_url': i['share_info']['share_url'],
                        'content': i['desc'], 'nick_name': i['author']['nickname'],
                        'signature': i['author']['signature'].replace("\n", ''), 'post_time_ts': i['create_time'],
                        'post_time': DateTimeHelper.format_datetime(i['create_time'], "%Y-%m-%d %H:%M:%S").split(" ")[
                            0], 'like_num': i['statistics']['digg_count'],
                        'download_num': i['statistics']['download_count'], 'share_num': i['statistics']['share_count'],
                        'forward_num': i['statistics']['forward_count'],
                        'comment_num': i['statistics']['comment_count'], 'sec_uid': str(i['author']['sec_uid']),
                        'user_id': str(i['author_user_id']),
                        'user_url': 'https://www.iesdouyin.com/share/user/{user_id}?sec_uid={sec_uid}'.format(
                            user_id=str(i['author_user_id']), sec_uid=str(i['author']['sec_uid'])),
                        'task_uuid': task.get('task_uuid'), 'stage_uuid': task.get('stage_uuid'),
                        'keyword': task.get('keyword')}
                crawler_redbook_user.apply_async((info,))
    # else:
    #     # 采集失败回调重复采集
    #     # TODO 可能会死循环，重试次数需要限制
    #     crawler_douyin.apply_async((task,))
    # app.send_task('app.redbook', [task])


@app.task(name="douyin.douyin.user")
def crawler_redbook_user(info):
    sec_uid = info['sec_uid']
    info = SpiderDouyin.spider_user(sec_uid, info)
    print(info)
    producer.send('douyin', value=bytes(json.dumps(info, ensure_ascii=False), encoding='utf8'))
    producer.flush()


if __name__ == '__main__':
    print(json.dumps(SpiderDouyin.spider_list('oppo', 1)))
