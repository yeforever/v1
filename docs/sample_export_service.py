#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@version: 1.0
@author: anne
@contact: thy.self@foxmail.com
@time: 2019/8/13 18:02
"""
import os

from boost_py.helpers.core.datetime_helper import DateTimeHelper
from openpyxl import Workbook

from src.commons.logging_helper import LoggingHelper
from src.config.main import analysis_config
from src.config.main import dir_config

from src.models.mongodb.dts_datawarehouse import BriefTaskMweiboArticleCollections
from src.models.mysql.dts_models import AutoBriefTask

# 制定日志输出log名
APP_NAME = 'XXX_export_service'
logger = LoggingHelper.get_logger(app_name=APP_NAME)


class XXXExportService(object):
    """
    工单导出，根据job_uuid 批量导出
    """

    # 定义标题
    TITLE = ['微博链接', '关键词', '微博内容', '发布时间', '发布时间戳', '转发数', '评论数', '点赞数', '账号ID', '账号链接', '账号名称',
             '账号粉丝数', '账号关注数', '账号发布微博数', '总转发数', '总评论数', '总点赞数']

    @classmethod
    def data_export_excel(cls, task_uuid):
        """
        将task_uuid 相关的数据 从 mongodb 导出到 excel
        :param task_uuid:
        :return:
        """
        logger.info(f'task_uuid: {task_uuid} 的任务开始导出源数据')

        # 获取任务详情
        task = AutoBriefTask.select().where(AutoBriefTask.task_uuid == task_uuid)
        task_keyword = task[0].task_keyword
        task_limit_num = task[0].task_limit_num
        task_limit_starttime = task[0].task_limit_starttime
        task_limit_endtime = task[0].task_limit_endtime

        # todo 此处以mweibo 为例
        # 从mongodb 获取 task_uuid 采集到的数据
        result = list(BriefTaskMweiboArticleCollections().find(query_filter={
            'task_uuid': task_uuid,
            'post_time_ts': {
                "$gte": DateTimeHelper.parse_formatted_datetime(str(task_limit_starttime), fmt='%Y-%m-%d %H:%M:%S'),
                "$lte": DateTimeHelper.parse_formatted_datetime(str(task_limit_endtime), fmt='%Y-%m-%d %H:%M:%S')
            }
        }))

        """
        mongodb collections
        {
            "_id" : ObjectId("5e37c6f9d0a5c006417433ae"),
            "job_uuid" : "780e80d1-3fac-4c77-bdab-231e0ff76075",
            "task_uuid" : "61955405-b056-4626-b1c1-fc1509305c2c",
            "keyword" : "小白瓶",
            "post_time" : "2019-12-26 00:00:00",
            "post_time_ts" : 1577289600,
            "content" : "2020想要素颜也发光？生图也能打？必须备上OLAY小白瓶！光感小白瓶烟酰胺+Sepiwhite美白因子+Sepitonic矿物透亮因子深层焕亮肌肤，get白里透光肌。淡斑小白瓶国际美白专利搭配糖海带提取物精准狙击斑点瑕疵，带你走无瑕美白之路～OLAY天猫欢聚日来啦，趁着超值优惠赶紧上淘宝搜索【光感小白瓶】或【淡斑小白瓶】，还有超值大容量版不要错过哦~更多惊喜优惠等着你，快上淘宝搜索OLAY吧！http://t.cn/A6vYOi9N http://t.cn/A6vYOi90",
            "article_url" : "https://m.weibo.cn/detail/4453834639862072",
            "repost" : 43,
            "comment" : 107,
            "like" : 79,
            "user_id" : 1645365377,
            "user_url" : "https://weibo.com/1645365377",
            "user_name" : "OLAY",
            "fans_num" : 2272342,
            "follow_num" : 229,
            "post_num" : 13872,
            "all_repost" : 43,
            "all_comment" : 107,
            "all_like" : 79
        }
        """

        # 提取需要导出的数据，并按顺序放到list 中，提取limit_num需求部分的数据
        data = list(map(lambda x: [
            x['article_url'],
            x['keyword'],
            x['content'],
            x['post_time'],
            x['post_time_ts'],
            x['repost'],
            x['comment'],
            x['like'],
            x['user_id'],
            x['user_url'],
            x['user_name'],
            x['fans_num'],
            x['follow_num'],
            x['post_num'],
            x['all_repost'],
            x['all_comment'],
            x['all_like']
        ], result))[:task_limit_num]

        # excel 数据写入
        wb = Workbook()
        ws = wb.active
        ws.append(cls.TITLE)
        for info in data:
            try:
                ws.append(info)
            except Exception as e:
                # 错误级日志
                logger.error(e)
                pass
        try:
            wb.save(analysis_config['mweibo_cn'].format(keyword=task_keyword))
        except FileNotFoundError:
            if not os.path.exists(dir_config['data'] + '/mweibo'):
                os.mkdir(dir_config['data'] + '/mweibo')
                wb.save(analysis_config['mweibo_cn'].format(keyword=task_keyword))

        # task_uuid 采集数，更新到task 表中
        sum_task_num = len(data)
        AutoBriefTask.update({AutoBriefTask.sum_task_num: sum_task_num}).where(AutoBriefTask.task_uuid).execute()
        logger.info(f'{task_keyword}.xlsx 文件导出完成， 总共 {sum_task_num} 条数据')


if __name__ == '__main__':
    task_uuid = '9bbc7b66-6a69-4c62-ad4d-1eaae24c9183'
