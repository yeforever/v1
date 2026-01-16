"""
@version: 1.0
@author: yezi
@contact: yezi.self@foxmail.com
@time: 2021/11/4 下午5:03
"""
import json
import re
import time
from datetime import timedelta, datetime
from urllib.parse import quote

import requests
from celery import Celery

from src.commons.datatime_helper import DateTimeHelper
from src.commons.exception_helper import merry_except
from src.config.main import redis_config
from src.commons.kafka_helper import producer

"""
celery 多进程连接mysql 可能出现并发问题，这里使用kafka解决，将数据发到kafka, 由kafka 消费者来消费数据写入数据库
"""


class SpiderMweibo(object):
    """
    微博平台采集
    """
    # 关键词数据获取接口
    INDEX_URL = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D{keyword}' \
                '&page_type=searchall&page={page}'
    # 开始页
    START_PAGE = 1

    # 标识无数据页面特征
    NO_TEXT_MSG = {'ok': 0, 'msg': '这里还没有内容', 'data': {'cards': []}}

    # 伪装的请求头
    HEADERS = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                      '/49.0.2623.110 Safari/537.36'
    }

    @classmethod
    def format_weibo_posttime(cls, date):
        if re.match('刚刚', date):
            date = DateTimeHelper.format_datetime(int(time.time()))
        elif re.match(r'\d+秒', date):
            second = re.match(r'(\d+)', date).group(1)
            second = timedelta(seconds=int(second))
            date = (datetime.now() - second).strftime('%Y-%m-%d %H:%M:%S')
        elif re.match(r'\d+分钟前', date):
            minute = re.match(r'(\d+)', date).group(1)
            date = DateTimeHelper.format_datetime(int(time.time()) - 60 * int(minute))
        elif re.match(r'\d+小时前', date):
            hour = re.match(r'(\d+)', date).group(1)
            date = DateTimeHelper.format_datetime(int(time.time()) - 60 * 60 * int(hour))
        elif re.match('昨天.*', date):
            date = re.match('昨天(.*)', date).group(1).strip()
            date = DateTimeHelper.format_datetime(int(time.time()) - 24 * 60 * 60, '%Y-%m-%d') + ' ' + date + ":00"
        elif re.match('今天.*', date):
            date = re.match('今天(.*)', date).group(1).strip()
            date = DateTimeHelper.format_datetime(int(time.time()), '%Y-%m-%d') + ' ' + date + ":00"
        elif re.match(r'\d{1,2}-\d{1,2}', date):
            date = time.strftime('%Y-', time.localtime()) + date + ' 00:00:00'
            date = DateTimeHelper.format_datetime(DateTimeHelper.parse_formatted_datetime(date, '%Y-%m-%d %H:%M:%S'))
        elif re.match(r'\d{4}-\d{1,2}-\d{1,2}', date):
            date = date.split(' ')[0] + ' 00:00:00'
            date = DateTimeHelper.format_datetime(DateTimeHelper.parse_formatted_datetime(date, '%Y-%m-%d %H:%M:%S'))
        elif re.match(r'\d{1,2}月\d{1,2}日', date):
            date = time.strftime('%Y-', time.localtime()) + date.replace('月', '-').replace('日', '') + ' 00:00:00'
            date = DateTimeHelper.format_datetime(DateTimeHelper.parse_formatted_datetime(date, '%Y-%m-%d %H:%M:%S'))
        elif re.match(r'\d{4}年\d{1,2}月\d{1,2}日', date):
            date = date.split(' ')[0].replace('年', '-').replace('月', '-').replace('日', '') + ' 00:00:00'
            date = DateTimeHelper.format_datetime(DateTimeHelper.parse_formatted_datetime(date, '%Y-%m-%d %H:%M:%S'))
        return date

    @classmethod
    @merry_except
    def spider_html(cls, keyword, page):
        # TODO 采集失败，需要重试
        requests.packages.urllib3.disable_warnings()
        keyword = quote(keyword)
        # print(cls.INDEX_URL.format(keyword=keyword, page=page))
        html = requests.get(url=cls.INDEX_URL.format(keyword=keyword, page=page), timeout=2,
                            headers=cls.HEADERS, verify=False)

        data = html.json()
        # print(data)
        if html == cls.NO_TEXT_MSG:
            data = {}
        else:
            data = cls.parse_html(data)
        return data

    @classmethod
    @merry_except
    def parse_html(cls, html):
        result = []
        if 'data' in html.keys() and 'cards' in html['data'].keys():
            for each_data in html['data']['cards']:
                if 'card_group' in each_data.keys():
                    if not each_data['card_group']:
                        continue
                    for x in each_data['card_group']:
                        if 'mblog' not in x.keys():
                            continue
                        each_data = x
                        if '全文</a>' in each_data['mblog']['text']:
                            if each_data["mblog"].get("raw_text"):
                                each_data['mblog']['text'] = each_data['mblog']['raw_text']
                        result.append(each_data)
                else:
                    if "mblog" not in each_data.keys():
                        continue
                    if '全文</a>' in each_data['mblog']['text']:
                        if each_data["mblog"].get("raw_text"):
                            each_data['mblog']['text'] = each_data['mblog']['raw_text']
                    result.append(each_data)
        return result


app = Celery(
    'weibo',
    backend=f'redis://:{redis_config["password"]}@{redis_config["host"]}:{redis_config["port"]}/14',
    broker=f'redis://:{redis_config["password"]}@{redis_config["host"]}:{redis_config["port"]}/15'
)


#  celery -A src.services.worker.mweibo_worker.app worker -l info -P gevent -c 60
@app.task(name="weibo.weibo")
def crawler_weibo(task):
    # task = json.loads(task)
    # f = lambda x: int(x) if '万' not in x else int(float(x.replace('万', '')) * 10000)
    # print(task)
    def f(x):
        return int(x) if '万' not in x else int(float(x.replace('万', '')) * 10000)
    su = SpiderMweibo.spider_html(task.get('keyword'), task.get('page'))
    # print(su)
    for each_data in su:
        post_ts = DateTimeHelper.parse_formatted_datetime(each_data['mblog']['created_at'],
                                                          "%a %b %d %H:%M:%S +0800 %Y")
        print(DateTimeHelper.format_datetime(post_ts))
        if task.get('start_ts') <= post_ts <= task.get('end_ts'):
            info = {'post_time': DateTimeHelper.format_datetime(post_ts), 'post_time_ts': post_ts,
                    'content': re.sub(re.compile(r'<.*?>'), '', each_data['mblog']['text']),
                    'note_id': each_data['mblog']['id'], 'repost': each_data['mblog']['reposts_count'],
                    'comment': each_data['mblog']['comments_count'], 'like': each_data['mblog']['attitudes_count'],
                    'user_id': each_data['mblog']['user']['id'], 'user_name': each_data['mblog']['user']['screen_name'],
                    'is_repost': 1 if 'repost_type' in each_data['mblog'].keys() else 0,
                    'fans': f(each_data['mblog']['user']['followers_count']),
                    'follow': each_data['mblog']['user']['follow_count'],
                    'post': each_data['mblog']['user']['statuses_count'], 'task_uuid': task.get('task_uuid'),
                    'stage_uuid': task.get('stage_uuid'), 'keyword': task.get('keyword')}
            # MysqlSave.save_weibo(task.get('task_uuid'), info)
            # print(info)
            producer.send('weibo', value=bytes(json.dumps(info, ensure_ascii=False), encoding='utf8'))
            producer.flush()

    # todo 所有平台需要有触发导出的逻辑， 第20页结束
    # if task.get('page') == 2:
    #     time.sleep(5)
    #     # 通过http 请求的方式，触发文件导出
    #     requests.get(f"http://0.0.0.0:9001/export?task_uuid={task.get('task_uuid')}&platform_name=mweibo")
