"""
@version: 1.0
@author: yezi
@contact: yezi.self@foxmail.com
@time: 2021/11/4 下午5:03
"""
import json
import re
from math import log

from celery import Celery

from src.commons.datatime_helper import DateTimeHelper
from src.commons.exception_helper import merry_except
from src.commons.kafka_helper import producer
from src.commons.whosecard_open_platform import WhosecardXhsSpider
from src.config.main import redis_config


class SpiderRedbook(object):
    """
    小红书平台采集
    """

    @classmethod
    @merry_except
    def spider_list(cls, keyword, page):
        data = WhosecardXhsSpider.get_search_notes(keyword, page)
        if not data.get('cost'):
            return {}
        else:
            return data

    @classmethod
    @merry_except
    def spider_note(cls, note_id):
        data = WhosecardXhsSpider.get_note_detail(note_id)
        if not data.get('cost'):
            return {}
        else:
            return data

    @classmethod
    @merry_except
    def spider_user(cls, user_id):
        data = WhosecardXhsSpider.get_user_info(user_id)
        if not data.get('cost'):
            return {}
        else:
            return data


app = Celery(
    'redbook',
    backend=f'redis://:{redis_config["password"]}@{redis_config["host"]}:{redis_config["port"]}/12',
    broker=f'redis://:{redis_config["password"]}@{redis_config["host"]}:{redis_config["port"]}/13'
)


#  celery -A src.services.worker.redbook_worker.app worker -l info -P gevent -c 60
@app.task(name="redbook.redbook")
def crawler_redbook(task):
    # task = json.loads(task)
    su = SpiderRedbook.spider_list(task.get('keyword'), task.get('page'))
    if su:
        # TODO  解析json,筛选ids
        # 筛选文章，有ads的元素是插入的广告，需要过滤掉
        notes = list(filter(lambda x: x.get('model_type') == 'note', su.get('result').get('data').get('items')))
        # f = lambda x: int(x, 16)
        # 筛选符合下单要求的时间段内的文章，不是的就过滤掉
        ids = list(
            filter(lambda x: task.get('start_ts') <= int(x.get('note').get('id')[:8], 16) <= task.get('end_ts'), notes))
        for i in ids:
            # print(i.get('note').get('id'))
            # print(f(i.get('note').get('id')[:8]))
            show = dict()
            show['task_uuid'] = task.get('task_uuid')
            show['stage_uuid'] = task.get('stage_uuid')
            show['keyword'] = task.get('keyword')
            show['id'] = i.get('note').get('id')
            # 将id 发往下游的采集处理
            # app.send_task('app.redbook.note', [i.get('note').get('id')])
            crawler_redbook_note.apply_async((show,))
            # crawler_redbook_user.apply_async((i.get('note').get('user').get('userid'),))
    # else:
    #     # 采集失败回调重复采集
    #     # TODO 可能会死循环，重试次数需要限制
    #     crawler_redbook.apply_async((task,))
        # app.send_task('app.redbook', [task])

    # producer = KafkaProducer(bootstrap_servers="0.0.0.0:9092")
    # producer.send('note', value=bytes(json.dumps(su, ensure_ascii=False), encoding='utf8'))
    # producer.flush(5)


@app.task(name="redbook.redbook.note")
def crawler_redbook_note(show):
    # task = json.loads(task)
    note_id = show.get('id')
    data = SpiderRedbook.spider_note(note_id)
    if data:
        # TODO  解析json,将user_id发往下游采集
        note_url = 'https://www.xiaohongshu.com/discovery/item/' + data['result']['data'][0]['note_list'][0]['id']
        note_type = data['result']['data'][0]['note_list'][0]['type']
        if note_type == 'normal':
            note_type = '图文'
        note_title = repr(data['result']['data'][0]['note_list'][0]['share_info']['title'])
        note_title = re.sub(r'\\x[a-z0-9]{2}', '', note_title)[1:-1]
        note_content = repr(data['result']['data'][0]['note_list'][0]['desc'])
        note_content = re.sub(r'\\x[a-z0-9]{2}', '', note_content)[1:-1]
        note_post_time_ts = data['result']['data'][0]['note_list'][0]['time']
        note_post_time = DateTimeHelper.format_datetime(note_post_time_ts,
                                                        '%Y-%m-%d %H:%M:%S')
        note_like_num = data['result']['data'][0]['note_list'][0]['liked_count']
        note_comment_num = data['result']['data'][0]['note_list'][0]['comments_count']
        note_collect_num = data['result']['data'][0]['note_list'][0]['collected_count']
        note_share_num = data['result']['data'][0]['note_list'][0]['shared_count']
        note_collect_like_num = note_like_num + note_collect_num
        # note_like_num、note_comment_num、note_collect_num可能为负值引发ValueError,已在上层捕获
        score = round(
            (0.2 * (pow(log(int(note_like_num) + 1), 2)) + 0.4 * (pow(log(int(note_comment_num) + 1), 2)) + 0.4 * (
                pow(log(int(note_collect_num) + 1), 2))), 2)

        if data['result']['data'][0]['note_list'][0]['ats']:
            note_ats = [data['result']['data'][0]['note_list'][0]['ats'][i]['nickname'] for i in
                        range(len(data['result']['data'][0]['note_list'][0]['ats']))]
        else:
            note_ats = []

        note_tags = note_ats
        note_tag = []
        for i in note_tags:
            if isinstance(i, dict):
                note_tag.append(i['name'])
            else:
                note_tag.append(i)
        note_tag = note_tag
        user_detail = data['result']['data'][0]['user']
        user_name = user_detail['nickname']  # 用户名
        user_url = f'https://www.xiaohongshu.com/user/profile/{user_detail["id"]}'
        info = {'user_url': user_url, 'user_id': user_detail["id"], 'user_name': user_name, 'note_url': note_url,
                'note_type': note_type, 'note_title': note_title, 'note_content': note_content,
                'note_post_time': note_post_time, 'note_post_time_ts': note_post_time_ts,
                'note_like_num': note_like_num, 'note_comment_num': note_comment_num,
                'note_collect_num': note_collect_num, 'note_share_num': note_share_num,
                'note_collect_like_num': note_collect_like_num,
                'note_interaction_sum': note_like_num + note_collect_num + note_share_num + note_comment_num,
                'score': score, 'note_cooperate_binds': '', 'note_tags': str(note_tag),
                'task_uuid': show.get('task_uuid'), 'stage_uuid': show.get('stage_uuid'),
                'keyword': show.get('keyword')}
        print(info['user_name'])
        # app.send_task('app.redbook.user', [user_id, info])
        crawler_redbook_user.apply_async((info,))

    # else:
    #     # app.send_task('app.redbook.note', [note_id])
    #     crawler_redbook_note.apply_async((note_id,))


@app.task(name="redbook.redbook.user")
def crawler_redbook_user(info):
    # task = json.loads(task)
    user_id = info.get('user_id')
    su = SpiderRedbook.spider_user(user_id)
    if su:
        user_info = su['result']['data']
        user_fans_num = user_info['fans']
        if 0 <= user_fans_num <= 50000:
            user_fans_level = '素人'
        elif 50000 <= user_fans_num <= 200000:
            user_fans_level = '底部kol'
        elif 200000 <= user_fans_num <= 1000000:
            user_fans_level = '腰部kol'
        else:
            user_fans_level = '头部kol'
        user_follow_num = user_info['follows']
        user_like_num = user_info['liked']
        user_collected_num = user_info['collected']
        user_note_num = user_info['ndiscovery']
        user_location = user_info['location']
        try:
            # 会报错
            user_level = user_info['level']['level_name']
            if not user_level:
                user_level = '无'
        except (KeyError, IndexError):
            user_level = '无'

        try:
            user_brief = repr(user_info['desc'])
            user_brief = re.sub(r'\\x[a-z0-9]{2}', '', user_brief)[1:-1]
        except (KeyError, IndexError):
            user_brief = '还没有简介'
        user_collect_like_num = user_collected_num + user_like_num

        info['user_brief'] = user_brief
        info['user_level'] = user_level
        info['user_location'] = user_location
        info['user_fans_num'] = user_fans_num
        info['user_fans_level'] = user_fans_level
        info['user_like_num'] = user_like_num
        info['user_follow_num'] = user_follow_num
        info['user_collected_num'] = user_collected_num
        info['user_collect_like_num'] = user_collect_like_num
        info['user_all_note_num'] = user_note_num
        info['note_interaction_per'] = round(
            (info['note_like_num'] + info['note_collect_num'] + info['note_share_num'] + info[
                'note_comment_num']) / user_fans_num, 2)
        print(info)

        producer.send('redbook', value=bytes(json.dumps(info, ensure_ascii=False), encoding='utf8'))
        producer.flush()

    # else:
    #     # app.send_task('app.redbook.user', [info])
    #     crawler_redbook_user.apply_async((info,))
