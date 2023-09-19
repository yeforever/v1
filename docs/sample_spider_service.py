#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@version: 1.0
@author: anne
@contact: thy.self@foxmail.com
@time: 2019/8/13 18:02
"""
import re
import requests
from boost_py.helpers.core.datetime_helper import DateTimeHelper

from src.commons.logging_helper import LoggingHelper
from src.models.mongodb.dts_datawarehouse import BriefTaskMweiboArticleCollections
from src.models.mysql.dts_models import AutoBriefTask

APP_NAME = 'xxx_spider_service'
logger = LoggingHelper.get_logger(APP_NAME)


class SpiderXXX(object):
    """
    XXX平台采集
    """
    # 关键词数据获取接口
    INDEX_URL = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D{keyword}' \
                '&page_type=searchall&page={page}'
    # 开始页
    START_PAGE = 1

    # 结束页
    MAX_PAGE = 100

    # 测试可以设置为2，提高测试效率
    # MAX_PAGE = 2

    # 标识无数据页面特征
    NO_TEXT_MSG = {'ok': 0, 'msg': '这里还没有内容', 'data': {'cards': []}}

    # 伪装的请求头
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                      '/49.0.2623.110 Safari/537.36'
    }

    # todo 其他公共可提取的参数

    # 有需要代理的项目，封装一个获取代理ip的方法
    @classmethod
    def get_ip(cls):
        """
        有需要代理的项目，封装一个获取代理ip的方法
        :return:
        """
        proxy_url = "http://dynamic.goubanjia.com/dynamic/get/20634b1d5aeedeb44b5af6bb1699cb29.html?sep=3"
        proxy_ip = requests.get(proxy_url).text.replace("\n", "")
        proxy = {
            "http": proxy_ip,
            "https": proxy_ip
        }
        return proxy

    # 获取html数据
    @classmethod
    def get_html(cls, page_num, keyword):
        """
        获取html数据
        :param page_num:
        :param keyword:
        :return:
        """
        try:
            html = requests.get(url=cls.INDEX_URL.format(keyword=keyword, page=str(page_num)),
                                headers=cls.headers)
            data = html.json()
            if html == cls.NO_TEXT_MSG:
                return {}
            else:
                return data
        except Exception as e:
            logger.error(e)
            # TODO 采集失败异常处理方案
            pass
            return {}

    @classmethod
    def parse_html(cls, html):
        """解析response_html

        :param html:
        :return:
        """
        data = []
        if 'data' in html.keys() and 'cards' in html['data'].keys():
            for each_data in html['data']['cards']:
                if 'card_group' in each_data.keys():
                    for x in each_data['card_group']:
                        if 'mblog' not in x.keys():
                            continue
                        each_data = x
                        if '全文</a>' in each_data['mblog']['text']:
                            each_data['mblog']['text'] = each_data['mblog']['longText']['longTextContent']
                        data.append(each_data)
                else:
                    if '全文</a>' in each_data['mblog']['text']:
                        each_data['mblog']['text'] = each_data['mblog']['longText']['longTextContent']
                    data.append(each_data)
                    # todo 此处以mweibo 为例
                    data = [{
                        'post_time': cls.time_fix(i['mblog']['created_at']),
                        'post_time_ts': DateTimeHelper.parse_formatted_datetime(cls.time_fix(i['mblog']['created_at']),
                                                                                fmt='%Y-%m-%d %H:%M:%S'),
                        'content': re.sub(re.compile(r'<.*?>'), '', i['mblog']['text']),
                        'article_url': 'https://m.weibo.cn/detail/' + i['mblog']['id'],
                        'repost': i['mblog']['reposts_count'],
                        'comment': i['mblog']['comments_count'],
                        'like': i['mblog']['attitudes_count'],
                        'user_id': i['mblog']['user']['id'],
                        'user_url': 'https://weibo.com/' + str(i['mblog']['user']['id']),
                        'user_name': i['mblog']['user']['screen_name'],
                        'fans_num': i['mblog']['user']['followers_count'],
                        'follow_num': i['mblog']['user']['follow_count'],
                        'post_num': i['mblog']['user']['statuses_count'],
                        'all_repost': i['mblog']['reposts_count'],
                        'all_comment': i['mblog']['comments_count'],
                        'all_like': i['mblog']['attitudes_count']
                    } for i in data]
        else:
            data = []
        return data

    @classmethod
    def save_to_mongodb(cls, job_uuid, task_uuid, keyword, data):
        if data:
            BriefTaskMweiboArticleCollections().insert_many([{
                'job_uuid': job_uuid,
                'task_uuid': task_uuid,
                'keyword': keyword,
                'post_time': i['post_time'],
                'post_time_ts': i['post_time_ts'],
                'content': i['content'],
                'article_url': i['article_url'],
                'repost': i['repost'],
                'comment': i['comment'],
                'like': i['like'],
                'user_id': i['user_id'],
                'user_url': i['user_url'],
                'user_name': i['user_name'],
                'fans_num': i['fans_num'],
                'follow_num': i['follow_num'],
                'post_num': i['post_num'],
                'all_repost': i['all_repost'],
                'all_comment': i['all_comment'],
                'all_like': i['all_like']
            } for i in data])

    @classmethod
    def spider_all_page_for(cls, job_uuid, task_uuid, keyword):
        """
        通过生成器翻页，采集所有页面数据
        :return:
        """

        def spider_next_page(page_num):
            next_page = cls.START_PAGE
            proxy = cls.get_ip()

            while next_page < page_num:
                html = cls.get_html(page_num=next_page, keyword=keyword)

                next_page += 1
                # 如果采集成功且有下一页 跳转下一页
                if html:
                    yield html
                # 如果采集失败或者没有下一页，跳出
                else:
                    break

        for i in spider_next_page(cls.MAX_PAGE):
            page_html = i
            try:
                # 解析页面
                data = cls.parse_html(page_html)
                # 存储数据
                cls.save_to_mongodb(job_uuid, task_uuid, keyword, data)
            except Exception as e:
                logger.error(e)
                continue

    @classmethod
    def spider_keywords(cls, task_uuid):
        """单线程采集关键词列表

        :param task_uuid:
        :return:
        """
        task = AutoBriefTask.select().where(AutoBriefTask.task_uuid == task_uuid)
        job_uuid = task[0].job_uuid
        task_platform = task[0].platform_code
        task_keyword = task[0].task_keyword
        task_limit_num = task[0].task_limit_num
        task_limit_starttime = task[0].task_limit_starttime
        task_limit_endtime = task[0].task_limit_endtime
        if task_platform == 2 and task_limit_starttime == '' and task_limit_endtime == '' and task_limit_num < 1000:
            # TODO 如果微博平台，无时间限制要求，只要前100条速度要快的需求下，可以在采集时只去 采集到 task_limit_num 就结束
            for i in range(1, task_limit_num / 10 + 1):
                page_html = cls.get_html(page_num=i, keyword=task_keyword)
                try:
                    # 解析页面
                    data = cls.parse_html(page_html)
                    # 存储数据
                    cls.save_to_mongodb(job_uuid, task_uuid, task_keyword, data)
                except Exception as e:
                    logger.error(e)
                    continue
        else:
            # 如果不是，则全部采集，export再处理
            cls.spider_all_page_for(job_uuid, task_uuid, task_keyword)


if __name__ == '__main__':
    SpiderXXX.spider_keywords(task_uuid='')
