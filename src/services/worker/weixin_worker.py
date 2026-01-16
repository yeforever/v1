"""
@version: 1.0
@author: yezi
@contact: yezi.self@foxmail.com
@time: 2021/11/4 下午5:03
"""
import json
import re

import requests
from celery import Celery

from src.commons.datatime_helper import DateTimeHelper
from src.commons.exception_helper import merry_except
from src.config.main import redis_config
from src.commons.kafka_helper import producer


class WeiXinParser(object):

    @classmethod
    def string_purge(cls, content):
        """清洗字符串，去除unicode编码

        :param content:
        :return:
        """
        content = repr(''.join(str(content)))
        content = re.sub(r'\\[uU][0-9a-z]+', '', content)[1: -1]
        return content

    @classmethod
    def parse_sogou_weixin_account_search_item(cls, item_account, cookie):
        """ 解析来自搜狗微信公众号搜索中搜索结果

        :param item_account:
        :param cookie:
        :return:
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/87.0.4280.141 Safari/537.36",
            "Cookie": cookie
        }
        account_url = "https://weixin.sogou.com" + item_account["anti"]["account"]
        resp = requests.get(account_url, headers=headers).json()
        msg = resp["msg"]
        accounts = []
        items = item_account["items"]
        for i in items:
            try:
                new_id = re.findall(r'<id><!\[CDATA\[(.*)]]></id>', i, re.S)
                if msg.get(new_id[0]):
                    post_num = msg[new_id[0]].split(",")[0]
                else:
                    post_num = 0
                account_name = re.findall(r'<name><!\[CDATA\[(.*)]]></name>', i, re.S)[0]
                account_name = cls.string_purge(account_name)
                account_code = re.findall(r'<weixinhao><!\[CDATA\[(.*)]]></weixinhao>', i, re.S)[0]
                account_code = cls.string_purge(account_code)
                fans_num = 0
                signature = re.findall(r'<summaryfull><!\[CDATA\[(.*)]]></summaryfull>', i, re.S)[0]
                signature = cls.string_purge(signature)
                verify = re.findall(r'<authfull><!\[CDATA\[(.*)]]></authfull>', i, re.S)
                verify = verify[0] if verify else ""
                verify = cls.string_purge(verify)
                article_title = re.findall(r'<news>.*<title><!\[CDATA\[(.*)]]></title>.*</news>', i, re.S)
                article_title = article_title[0] if article_title else ""
                article_title = cls.string_purge(article_title)
                content = re.findall(r'<news>.*<content><!\[CDATA\[(.*)]]></content>.*</news>', i, re.S)
                content = content[0] if content else ""
                content = cls.string_purge(content)
                article_time = re.findall(r'<news>.*<date><!\[CDATA\[(.*)]]></date>.*</news>', i, re.S)
                article_time = article_time[0] if article_time else ""
                result = {
                    "account_name": account_name,
                    "account_code": account_code,
                    "fans_num": fans_num,
                    "post_num": post_num,
                    "signature": signature,
                    "verify": verify,
                    "article_title": article_title,
                    "content": content,
                    "article_time": article_time
                }
                accounts.append(result)
            except IndexError:
                continue
        return accounts

    @classmethod
    def parse_sogou_weixin_article_search_item(cls, item_content):
        """ 解析来自搜狗微信文章搜索中搜索结果

        :param item_content:
        :return:
        """
        item = {
            'title': {'regex': r'<title><\!\[CDATA\[(.*)\]\]></title>', 'value': ''},  # 标题
            'imglink': {'regex': r'<imglink><\!\[CDATA\[(.*)\]\]></imglink>', 'value': ''},  # 文章封面
            'headimage': {'regex': r'<headimage><\!\[CDATA\[(.*)\]\]></headimage>', 'value': ''},  # 公众号头像
            'sourcename': {'regex': r'<sourcename><\!\[CDATA\[(.*)\]\]></sourcename>', 'value': ''},  # 公众号名称
            'content168': {'regex': r'<content168><\!\[CDATA\[(.*)\]\]></content168>', 'value': ''},  # 文章简介
            'username': {'regex': r'<username><\!\[CDATA\[(.*)\]\]></username>', 'value': ''},  # 公众号id
            'readnum': {'regex': r'<readnum>(\w+)</readnum>', 'value': ''},  # 阅读数
            'forwardnum': {'regex': r'<forwardnum>(\w+)</forwardnum>', 'value': ''},  # 点赞数
            'openid': {'regex': r'<openid><\!\[CDATA\[(.*)\]\]></openid>', 'value': ''},  # 微信的openid
            'shareUrl': {'regex': r'<encArticleUrl><\!\[CDATA\[(.*)\]\]></encArticleUrl>', 'value': ''},  # 文章链接
            'lastModified': {'regex': r'<lastModified>(\w+)</lastModified>', 'value': ''},  # 新建日期 1553567123
            'date': {'regex': r'<date><\!\[CDATA\[(.*)\]\]></date>', 'value': ''},  # 新建日期 如2018-6-4
            'source_url': {'regex': r'<site><\!\[CDATA\[(.*)\]\]></site>', 'value': ''}
        }

        for k, v in item.items():
            try:
                v["value"] = re.search(v["regex"], item_content).group(1)
            except AttributeError:
                pass
        formatted_post_date = DateTimeHelper.format_datetime(item['lastModified']['value'], '%Y-%m-%d')
        return {
            'openid': item['openid']['value'],
            'weixin_id': item['username']['value'],
            'article_cover_img': item['imglink']['value'],
            'weixin_nickname': item['sourcename']['value'],
            'account_avatar_img': item['headimage']['value'],
            'profile_url': '',
            'account_biz_code': '',
            'article_sn_code': '',
            'article_mid_code': '',
            'title': item['title']['value'],
            'has_video': 0,
            'article_url': item['shareUrl']['value'],
            'article_short_desc': item['content168']['value'],
            'article_source_url': item['source_url']['value'],
            'is_orig': '',
            'article_pos': '',
            'article_post_time': int(item['lastModified']['value']),
            'article_post_date': DateTimeHelper.parse_formatted_datetime(item['date']['value'], '%Y-%m-%d'),
            'article_formatted_post_time': DateTimeHelper.format_datetime(item['lastModified']['value']),
            'article_formatted_post_date': formatted_post_date,
            'read_num': int(item['readnum']['value']),
            'like_num': int(item['forwardnum']['value'])
        }


class SpiderWeixin(object):
    INDEX_URL = 'https://weixin.sogou.com/weixinwap?page={page}&total_pages=1&_rtype=json&' \
                'query={keyword}&type=2&ie=utf8&_sug_=n&_sug_type_=-1&s_from=input'
    cookies = ''

    @classmethod
    @merry_except
    def spider_list(cls, keyword, page):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/87.0.4280.66 Safari/537.36",
            'Cookie': cls.cookies}
        next_url = cls.INDEX_URL.format(keyword=keyword, page=str(page))
        resp = requests.get(next_url, headers=headers, allow_redirects=False)
        html = resp.content.decode()

        # capt = re.findall(r'totalItems', html)
        return html

        # # todo 如果触发验证码 当前所有微信工单都只采集100条， 1000条需要接入验证码逻辑，把获取新cookie 做成接口，出现问题时 发送请求解决
        # while not capt:
        #     location = resp.headers["Location"]
        #     result = CaptchaSolve.init_captcha(location, cookies=cookies)
        #     cookie = result["cookie"]
        #     headers["Cookie"] = cookie
        #     resp = requests.get(next_url, headers=headers, allow_redirects=False)
        #     html = resp.content.decode()
        #     capt = re.findall(r'totalItems', html)


app = Celery(
    'weixin',
    backend=f'redis://:{redis_config["password"]}@{redis_config["host"]}:{redis_config["port"]}/10',
    broker=f'redis://:{redis_config["password"]}@{redis_config["host"]}:{redis_config["port"]}/11'
)


#  celery -A src.services.worker.weixin_worker.app worker -l info -P gevent -c 60
@app.task(name="weixin.weixin")
def crawler_weixin(task):
    data = SpiderWeixin.spider_list(task.get('keyword'), task.get('page'))
    for i in json.loads(data)['items']:
        try:
            article = WeiXinParser.parse_sogou_weixin_article_search_item(i)
        except KeyError:
            continue
        article_content = article['article_short_desc']
        title = repr(article['title'])
        title = re.sub(r'\\x[a-z0-9]{2}', '', title)
        title = re.sub(r'\\[uU][0-9a-z]{4}', '', title)[1:-1]
        content = repr(article_content)
        content = re.sub(r'\\x[a-z0-9]{2}', '', content)
        content = re.sub(r'\\[uU][0-9a-z]{4}', '', content)[1:-1]
        ts = DateTimeHelper.parse_formatted_datetime(article['article_formatted_post_time'], '%Y-%m-%d %H:%M:%S')
        if task.get('start_ts') <= ts <= task.get('end_ts'):
            info = {
                'title': title,
                'content': content,
                'post_time': article['article_formatted_post_time'],
                'article_url': 'https://weixin.sogou.com' + article['article_url'],
                'article_pos': article['article_pos'],
                'read_num': article['read_num'],
                'like_num': article['like_num'],
                'comment_num': -1,
                'weixin_nickname': article['weixin_nickname'],
                'weixin_id': article['weixin_id'],
                'fans_num': -1,
                'all_art_num': 1,
                'all_read_num': article['read_num'],
                'all_like_num': article['like_num'],
                'all_comment_num': -1
            }
            print(ts)
            info['task_uuid'] = task.get('task_uuid')
            info['stage_uuid'] = task.get('stage_uuid')
            info['keyword'] = task.get('keyword')
            # MysqlSave.save_weibo(task.get('task_uuid'), info)

            producer.send('weixin', value=bytes(json.dumps(info, ensure_ascii=False), encoding='utf8'))
            producer.flush()
