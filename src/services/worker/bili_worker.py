"""
@version: 1.0
@author: anne
@contact: thy.self@foxmail.com
@time: 2021/11/26 下午3:55
"""
import json
import urllib
from copy import deepcopy

import requests
from celery import Celery
from lxml import etree

from src.commons.datatime_helper import DateTimeHelper
from src.commons.exception_helper import merry_except
from src.config.main import redis_config
from src.commons.kafka_helper import producer


class SpiderBili(object):
    """
    b站平台采集
    """

    # INDEX_URL = 'https://search.bilibili.com/all?keyword={keyword}&page={page}'
    INDEX_URL = 'https://api.bilibili.com/x/web-interface/search/type?__refresh__=true&_extra=&context=&page={' \
                'page}&page_size=42&from_source=&from_spmid=333.337&platform=pc&highlight=1&single_column=0&keyword={' \
                'keyword}&category_id=&search_type=video&dynamic_offset=42&preload=true&com2co' \
                '=true '
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                      '/72.0.3626.121 Safari/537.36'
    }

    @classmethod
    def get_yuanren_ip(cls):
        url = "http://www.damaiip.com/index.php?s=/front/user/getIPlist&xsn=8c6827b0e0b286fee6e92e61fcc830c0&" \
              "osn=TC_NO16268668634575617"

        account = "womidata"
        password = "15216404695"
        resp = requests.get(url).text
        ip = resp.split(':')[0]
        port = resp.split(':')[1]
        proxies = {
            "http": f"http://{account}:{password}@{ip}:{port}",
            "https": f"https://{account}:{password}@{ip}:{port}"
        }
        return proxies

    @classmethod
    @merry_except
    def spider_list(cls, keyword, page):
        html = requests.get(url=cls.INDEX_URL.format(keyword=urllib.parse.quote(keyword), page=str(page)), headers=cls.HEADERS,
                            proxies=cls.get_yuanren_ip()).json()
        return html


app = Celery(
    'bili',
    backend=f'redis://:{redis_config["password"]}@{redis_config["host"]}:{redis_config["port"]}/18',
    broker=f'redis://:{redis_config["password"]}@{redis_config["host"]}:{redis_config["port"]}/19'
)


#  celery -A src.services.worker.bili_worker.app worker -l info -P gevent -c 60
@app.task(name="bili.bili")
def crawler_bili(task):
    html = SpiderBili.spider_list(task.get('keyword'), task.get('page'))
    # html_node = etree.HTML(html)
    # script_data = html_node.xpath('//script[contains(text(),"window.__INITIAL_STATE__")]/text()')
    if html['data']['result']:
        # article = script_data[0].replace(
        #     'window.__INITIAL_STATE__=', '').replace(
        #     ';(function(){var s;(s=document.currentScript||document.scripts[document.scripts.length-1]).parentNode.rem'
        #     'oveChild(s);}());', '').replace("False", "1").replace("True", "0").replace("None", "1")
        # user_json = json.loads(article)
        # fields_keyword = user_json["flow"]['fields'][0]
        # su = user_json['flow'][fields_keyword]["result"]
        su = html['data']['result']
        # 过滤
        if task.get('page') == 1:
            notes = list(filter(lambda k: k.get('result_type') == 'video', su))
            results = notes[0]['data']
        else:
            results = su
        for x in results:
            x["post_time"] = DateTimeHelper.format_datetime(x["pubdate"])
            x["post_time_ts"] = x['pubdate']

            if task.get('start_ts') <= x['pubdate'] <= task.get('end_ts'):
                x["title"] = x["title"].replace('<em class="keyword">', "").replace("\n", "|").replace(
                    "None",
                    "").replace(
                    "</em>", "")
                aid = x['id']
                info = deepcopy(x)
                info['aid'] = aid
                info['task_uuid'] = task.get('task_uuid')
                info['stage_uuid'] = task.get('stage_uuid')
                info['keyword'] = task.get('keyword')
                crawler_bili_user.apply_async((info,))

    # else:
    #     # 采集失败回调重复采集
    #     # TODO 可能会死循环，重试次数需要限制
    #     crawler_bili.apply_async((task,))


@app.task(name="bili.bili.user")
def crawler_bili_user(info):
    aid = info['aid']
    coin_url = f'https://api.bilibili.com/x/web-interface/archive/stat?aid={aid}'
    resp_coin = requests.get(coin_url, headers=SpiderBili.HEADERS, timeout=3).json()
    if resp_coin['message'] == '请求被拦截':
        resp_coin = requests.get(coin_url, headers=SpiderBili.HEADERS, proxies=SpiderBili.get_yuanren_ip(),
                                 timeout=2).json()

    if resp_coin['message'] != '请求被拦截':
        coin = resp_coin['data']['coin']
        like = resp_coin['data']['like']
        share = resp_coin['data']['share']
        info['coin'] = coin
        info['like'] = like
        info['share'] = share
        info['note_interaction_sum'] = coin + like + share
        mid = info['mid']
        info['pic'] = 'https:' + info['pic']
        author_url = f'https://space.bilibili.com/{mid}'
        info['user_url'] = author_url
        info['attention_url'] = f'https://api.bilibili.com/x/relation/stat?vmid={mid}'
        crawler_bili_note.apply_async((info,))
    # else:
    #     crawler_bili_user.apply_async((info,))


@app.task(name="bili.bili.note")
def crawler_bili_note(info):
    attention_url = info['attention_url']
    resp_attention = requests.get(attention_url, headers=SpiderBili.HEADERS, timeout=3).json()
    if resp_attention['message'] == '请求被拦截':
        resp_attention = requests.get(attention_url, headers=SpiderBili.HEADERS, proxies=SpiderBili.get_yuanren_ip(),
                                      timeout=2).json()

    if resp_attention['message'] != '请求被拦截':
        attention_num = resp_attention['data']['following']  # 用户关注数
        fans_num = resp_attention['data']['follower']  # 用户粉丝数

        info['attention_num'] = attention_num
        info['fans_num'] = fans_num
        # 删除无用数据
        info.pop('bvid')
        info.pop('hit_columns')
        info.pop('arcrank')
        info.pop('badgepay')
        info.pop('view_type')
        info.pop('is_pay')
        info.pop('is_union_video')
        info.pop('rec_tags')
        info.pop('pubdate')
        info.pop('new_rec_tags')
        info.pop('rank_score')
        info.pop('senddate')
        info.pop('typeid')
        info.pop('aid')
        info.pop('corner')
        info.pop('cover')
        info.pop('desc')
        info.pop('rec_reason')
        info.pop('url')
        print(info)

        # with open('xx.txt', 'a+', encoding='utf8') as f:
        #     f.write(json.dumps(info, ensure_ascii=False) + '\n')
        producer.send('bili', value=bytes(json.dumps(info, ensure_ascii=False), encoding='utf8'))
        producer.flush()
    # else:
    #     crawler_bili_note.apply_async((info,))
