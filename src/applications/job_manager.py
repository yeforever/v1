"""
@version: 1.0
@author: yezi
@contact: yezi.self@foxmail.com
@time: 2021/11/4 下午5:03
"""
import _thread
import json
import os
import time
import uuid
from typing import List

import uvicorn
from loguru import logger
from peewee import JOIN, fn
from pydantic import BaseModel
from fastapi import FastAPI, Query, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, StreamingResponse


from src.services.job_server import JobServer
from src.commons.datatime_helper import DateTimeHelper
from src.config.main import system_config
from src.commons.common_job_models_alias import wx, wb, rb, bi, dy, job, task, stage
from src.commons.common_response_error import err_2003, err_2004, err_2005, err_2006
from src.commons.common_job_params import platform_code_query, status_code, platform_code_zh, \
    platform_code_view_field_replace


APP_NAME = 'job_manage_application'
app = FastAPI()


class RespOkModel(BaseModel):
    err_code: int = 0
    err_msg: str = "success."
    data: dict = None


class RespErrModel(BaseModel):
    err_code: int = 1
    err_msg: str = "failed."
    data: dict = None


# 跨域共享列表，前后端不分离时跨域使用，前端词云图片http不能访问，会把http自动转换https, 所以接口http/https 需要互通
origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:8999",
    "https://localhost:8999"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许跨域请求的来源列表
    allow_credentials=True,  # 表示跨域请求支持cookie，默认False
    allow_methods=["*"],  # 跨域请求允许的http方法列表
    allow_headers=["*"],  # 跨域请求允许的请求头列表
)


# 添加请求头中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.post('/dts-auto-brief/job/submit')
async def submit_job(
        job_name: str = Query(...),
        job_desc: str = Query(...),
        create_user_name: str = Query(...),
        remarks: str = Query(default='')
):
    """
    提交任务
    :param remarks:
    :param job_name:娇韵诗关键词搜索
    :param job_desc: {"job_content": [{"endtime": 20200417, "keywords": "精华水/抗老/紧致/透亮/淡纹",
    "limitnum": 1000, "platform": "2", "starttime": 20190101}]}
    :param create_user_name: 汪赛楠
    :return:
    """
    # todo 优化判断
    logger.info("===================任务提交=====================")

    if len(str(job_name)) > 20:
        return err_2003
    if not isinstance(json.loads(job_desc)['job_content'], list):
        logger.info("传入job_content非list格式")
        return err_2004
    if len(json.loads(job_desc)['job_content']) > 5:
        logger.info(f"job_content长度大于5")
        return err_2005
    for i in json.loads(job_desc)['job_content']:
        if i.get('endtime') and i.get('keywords') and i.get('limitnum') and i.get('platform') and i.get('starttime'):
            continue
        else:
            return err_2006

    # 异步处理任务，同步情况延时1-2s, 异步2ms
    job_uuid = str(uuid.uuid4())
    _thread.start_new_thread(JobServer.submit_job_to_mysql, (job_uuid, job_desc, job_name, remarks, create_user_name,))
    # todo 企微推送通知
    logger.info(f'{job_uuid} 提交成功')

    return RespOkModel(
        data={
            'jobUuid': job_uuid,
            'jobName': job_name,
            'remarks': remarks,
            'jobContent': json.loads(job_desc)
        }
    )


# 功能弃用，java 端保留接口，此接口空逻辑
@app.post('/dts-auto-brief/job/cancel')
async def cancel_job(
        job_uuid: str = Query(...),
        cancel_reason: str = Query(...)
):
    """
    取消任务
    :param job_uuid:
    :param cancel_reason:
    :return:
    """
    # TODO  弃用使用伪代码
    logger.info(f"===================任务{job_uuid}取消失败=====================")

    return RespOkModel(
        data={
            'jobUuid': job_uuid,
            'jobReason': cancel_reason
        }
    )


# 功能弃用，java 端保留接口，此接口空逻辑
@app.post('/dts-auto-brief/job/spider_progress')
async def spider_progress(
        job_uuid: str = Query(...)
):
    """
    查看采集进度
    :param job_uuid:
    :return:
    """
    # TODO  下单即完成，没有查看进度功能，所以弃用改接口，使用伪代码
    logger.info(f"===================任务{job_uuid}需求更改失败=====================")

    return RespOkModel(
        data={
            'job_code': 'x',
            'create_user_name': 'x',
            'job_create_time': 'x',
            'executor_name': 'x',
            'job_wait_count': 'x',
            'job_status': 'x',
            'job_run_time': 'x'
        }
    )


# 弃用了不会调用此接口
@app.post('/dts-auto-brief/job/change')
async def change_job(
        job_uuid: str = Query(...),
        job_name: str = Query(...),
        job_desc: str = Query(...)
):
    """
    修改任务
    :param job_uuid:
    :param job_name:
    :param job_desc:
    :return:
    """
    # TODO  弃用使用伪代码
    logger.info(f"===================任务{job_uuid}需求更改失败=====================")
    return RespOkModel(
        data={
            'jobUuid': job_uuid,
            'job_name': job_name,
            'job_desc': job_desc
        }
    )


@app.post('/dts-auto-brief/job/view')
async def view_job(
        job_uuid: str = Query(...)
):
    """ 查看任务

    :param job_uuid:
    :return:
    """
    job_detail = job.select(
        job.job_name,
        job.job_desc,
        job.remarks).where(
        job.job_uuid == job_uuid
    )[0]
    job_name = job_detail.job_name
    job_remarks = job_detail.remarks

    # 拼接stage
    stage_query = stage.select(
        stage.stage_desc,
        stage.stage_name,
        stage.stage_status,
        stage.download_url,
        stage.stage_uuid).where(
        stage.job_uuid == job_uuid)
    print(stage_query)
    data = []
    for i in stage_query:
        stage_dict = dict()
        stage_dict['stageName'] = i.stage_name
        stage_uuid = i.stage_uuid
        stage_dict['stageUuid'] = stage_uuid
        stage_dict['stageStatus'] = "任务已完成"
        stage_dict['downloadUrl'] = i.download_url
        stage_dict['remarks'] = job_remarks
        stage_desc = eval(i.stage_desc)
        stage_dict['platforms'] = str([platform_code_zh[int(x)] for x in stage_desc['platform'].split('/')])[
                                  1:-1].replace(
            "'", '').replace(',', ';')
        start_time = DateTimeHelper.format_datetime(
            DateTimeHelper.parse_formatted_datetime(str(stage_desc['starttime']), '%Y%m%d'))
        end_time = DateTimeHelper.format_datetime(
            DateTimeHelper.parse_formatted_datetime(str(stage_desc['endtime']), '%Y%m%d'))

        stage_dict['stageRunTime'] = f'{start_time.split(" ")[0]}~{end_time.split(" ")[0]}'
        stage_dict['keywords'] = stage_desc['keywords'].replace('/', '、')
        stage_dict['limitNum'] = stage_desc['limitnum']
        data_list = []
        print(stage_desc['platform'].split('/'))
        for j in stage_desc['platform'].split('/'):
            stage_data = {}

            stage_path = f"{system_config['path']}/data/{stage_uuid}"
            content_img_url = f'http://brief.womdata.com/dts-auto-brief/img?stage_uuid={stage_uuid}&platform={j}' \
                              f'&img_type=1' if os.path.exists(f'{stage_path}/wc_{j}_1.png') else ''
            topic_img_url = f'http://brief.womdata.com/dts-auto-brief/img?stage_uuid={stage_uuid}&platform={j}' \
                            f'&img_type=2' if os.path.exists(f'{stage_path}/wc_{j}_2.png') else ''

            if j == '1':
                tasks_query = task.select(
                    task.task_uuid
                ).where(
                    task.stage_uuid == stage_uuid,
                    task.platform_code == 1
                )
                tasks = [i.task_uuid for i in tasks_query]
                query = wx.select(
                    fn.COUNT(wx.id).alias('article_sum_num'),
                    fn.COUNT(wx.user_name.distinct()).alias('account_sum_num'),
                    fn.SUM(wx.interaction).alias('article_interaction_sum_sum'),
                    fn.SUM(wx.like).alias('article_like_sum_num'),
                    fn.SUM(wx.read).alias('article_read_sum_num')
                ).where(
                    wx.task_uuid.in_(tasks)
                )[0]
                if query.article_sum_num:
                    stage_data = {
                        'article_sum_num': int(query.article_sum_num),
                        'account_sum_num': int(query.account_sum_num),
                        'article_interaction_sum_sum': int(query.article_interaction_sum_sum),
                        'article_like_sum_num': int(query.article_like_sum_num),
                        'article_read_sum_num': int(query.article_read_sum_num),
                        'platform': 1,
                        'content_img_url': content_img_url,
                        'topic_img_url': topic_img_url
                    }
                else:
                    stage_data = {
                        'article_sum_num': 0,
                        'account_sum_num': 0,
                        'article_interaction_sum_sum': 0,
                        'article_like_sum_num': 0,
                        'article_read_sum_num': 0,
                        'platform': 1,
                        'content_img_url': content_img_url,
                        'topic_img_url': topic_img_url
                    }
            elif j == '2':
                tasks_query = task.select(
                    task.task_uuid
                ).where(
                    task.stage_uuid == stage_uuid,
                    task.platform_code == 2
                )
                tasks = [i.task_uuid for i in tasks_query]
                query = wb.select(
                    fn.COUNT(wb.id).alias('article_sum_num'),
                    fn.COUNT(wb.user_name.distinct()).alias('account_sum_num'),
                    fn.SUM(wb.interaction).alias('article_interaction_sum_sum'),
                    fn.SUM(wb.comment).alias('article_comment_sum_num'),
                    fn.SUM(wb.like).alias('article_like_sum_num'),
                    fn.SUM(wb.share).alias('article_repost_sum_num')
                ).where(wb.task_uuid.in_(tasks))[0]
                # .join(tasks_query, JOIN.LEFT_OUTER, on=(tasks_query.c.task_uuid == wb.task_uuid))
                if query.article_sum_num:
                    stage_data = {
                        'article_sum_num': int(query.article_sum_num),
                        'account_sum_num': int(query.account_sum_num),
                        'article_interaction_sum_sum': int(query.article_interaction_sum_sum),
                        'article_comment_sum_num': int(query.article_comment_sum_num),
                        'article_like_sum_num': int(query.article_like_sum_num),
                        'article_repost_sum_num': int(query.article_repost_sum_num),
                        'platform': 2,
                        'content_img_url': content_img_url,
                        'topic_img_url': topic_img_url
                    }
                else:
                    stage_data = {
                        'article_sum_num': 0,
                        'account_sum_num': 0,
                        'article_interaction_sum_sum': 0,
                        'article_comment_sum_num': 0,
                        'article_like_sum_num': 0,
                        'article_repost_sum_num': 0,
                        'platform': 2,
                        'content_img_url': content_img_url,
                        'topic_img_url': topic_img_url
                    }
            elif j == '3':
                tasks_query = task.select(
                    task.task_uuid
                ).where(
                    task.stage_uuid == stage_uuid,
                    task.platform_code == 3
                )
                tasks = [i.task_uuid for i in tasks_query]
                query = rb.select(
                    fn.COUNT(rb.id).alias('article_sum_num'),
                    fn.COUNT(rb.user_name.distinct()).alias('account_sum_num'),
                    fn.SUM(rb.interaction).alias('article_interaction_sum_sum'),
                    fn.SUM(rb.note_collect_like_num).alias('article_collect_like_sum_num'),
                    fn.SUM(rb.collect).alias('article_collect_sum_num'),
                    fn.SUM(rb.comment).alias('article_comment_sum_num'),
                    fn.SUM(rb.like).alias('article_like_sum_num'),
                    fn.SUM(rb.share).alias('article_share_sum_num')
                ).where(rb.task_uuid.in_(tasks))[0]
                if query.article_sum_num:
                    stage_data = {
                        'article_sum_num': int(query.article_sum_num),
                        'account_sum_num': int(query.account_sum_num),
                        'article_interaction_sum_sum': int(query.article_interaction_sum_sum),
                        'article_collect_like_sum_num': int(query.article_collect_like_sum_num),
                        'article_collect_sum_num': int(query.article_collect_sum_num),
                        'article_comment_sum_num': int(query.article_comment_sum_num),
                        'article_like_sum_num': int(query.article_like_sum_num),
                        'article_share_sum_num': int(query.article_share_sum_num),
                        'platform': 3,
                        'content_img_url': content_img_url,
                        'topic_img_url': topic_img_url
                    }
                else:
                    stage_data = {
                        'article_sum_num': 0,
                        'account_sum_num': 0,
                        'article_interaction_sum_sum': 0,
                        'article_collect_like_sum_num': 0,
                        'article_collect_sum_num': 0,
                        'article_comment_sum_num': 0,
                        'article_like_sum_num': 0,
                        'article_share_sum_num': 0,
                        'platform': 3,
                        'content_img_url': content_img_url,
                        'topic_img_url': topic_img_url
                    }

            elif j == '4':
                tasks_query = task.select(
                    task.task_uuid
                ).where(
                    task.stage_uuid == stage_uuid,
                    task.platform_code == 4
                )
                tasks = [i.task_uuid for i in tasks_query]
                query = bi.select(
                    fn.COUNT(bi.id).alias('article_sum_num'),
                    fn.COUNT(bi.user_name.distinct()).alias('account_sum_num'),
                    fn.SUM(bi.interaction).alias('article_interaction_sum_sum'),
                    fn.SUM(bi.danmu).alias('article_barrage_sum_num'),
                    fn.SUM(bi.collect).alias('article_collect_sum_num'),
                    fn.SUM(bi.comment).alias('article_comment_sum_num'),
                    fn.SUM(bi.play).alias('article_play_sum_num')
                ).where(bi.task_uuid.in_(tasks))[0]
                if query.article_sum_num:
                    stage_data = {
                        'article_sum_num': int(query.article_sum_num),
                        'account_sum_num': int(query.account_sum_num),
                        'article_interaction_sum_sum': int(query.article_interaction_sum_sum),
                        'article_barrage_sum_num': int(query.article_barrage_sum_num),
                        'article_collect_sum_num': int(query.article_collect_sum_num),
                        'article_comment_sum_num': int(query.article_comment_sum_num),
                        'article_play_sum_num': int(query.article_play_sum_num),
                        'platform': 4,
                        'content_img_url': content_img_url,
                        'topic_img_url': topic_img_url
                    }
                else:
                    stage_data = {
                        'article_sum_num': 0,
                        'account_sum_num': 0,
                        'article_interaction_sum_sum': 0,
                        'article_barrage_sum_num': 0,
                        'article_collect_sum_num': 0,
                        'article_comment_sum_num': 0,
                        'article_play_sum_num': 0,
                        'platform': 4,
                        'content_img_url': content_img_url,
                        'topic_img_url': topic_img_url
                    }
            elif j == '5':
                tasks_query = task.select(
                    task.task_uuid
                ).where(
                    task.stage_uuid == stage_uuid,
                    task.platform_code == 5
                )
                tasks = [i.task_uuid for i in tasks_query]
                query = dy.select(
                    fn.COUNT(dy.id).alias('article_sum_num'),
                    fn.COUNT(dy.user_name.distinct()).alias('account_sum_num'),
                    fn.SUM(dy.interaction).alias('article_interaction_sum_sum'),
                    fn.SUM(dy.download).alias('article_download_sum_num'),
                    fn.SUM(dy.forward).alias('article_forward_sum_num'),
                    fn.SUM(dy.comment).alias('article_comment_sum_num'),
                    fn.SUM(dy.like).alias('article_like_sum_num')
                ).where(dy.task_uuid.in_(tasks))[0]
                if query.article_sum_num:
                    stage_data = {
                        'article_sum_num': int(query.article_sum_num),
                        'account_sum_num': int(query.account_sum_num),
                        'article_interaction_sum_sum': int(query.article_interaction_sum_sum),
                        'article_download_sum_num': int(query.article_download_sum_num),
                        'article_forward_sum_num': int(query.article_forward_sum_num),
                        'article_comment_sum_num': int(query.article_comment_sum_num),
                        'article_like_sum_num': int(query.article_like_sum_num),
                        'platform': 5,
                        'content_img_url': content_img_url,
                        'topic_img_url': topic_img_url
                    }
                else:
                    stage_data = {
                        'article_sum_num': 0,
                        'account_sum_num': 0,
                        'article_interaction_sum_sum': 0,
                        'article_download_sum_num': 0,
                        'article_forward_sum_num': 0,
                        'article_comment_sum_num': 0,
                        'article_like_sum_num': 0,
                        'platform': 5,
                        'content_img_url': content_img_url,
                        'topic_img_url': topic_img_url
                    }
            data_list.append(stage_data)
        stage_dict['data_list'] = data_list
        data.append(stage_dict)

    return RespOkModel(
        data={
            'jobUuid': job_uuid,
            'jobName': job_name,
            'data': data
        }

    )


@app.post('/dts-auto-brief/job/search')
async def search_all_job(
        job_name: str = Query(default=None),
        job_status: List[int] = Query(default=[]),
        job_platform: List[str] = Query(default=[]),
        page_offset: int = Query(default=10),
        page_size: int = Query(default=1),
        create_user_name: str = Query(None)
):
    """
    搜索所有task
    :param job_name:
    :param job_status:
    :param job_platform:
    :param page_offset:
    :param page_size:
    :param create_user_name:
    :return:
    """
    # 不带参数
    query = job.select(
        job.job_status,
        job.job_desc,
        job.job_created_time,
        job.job_name,
        job.job_code,
        job.job_uuid,
        job.cancel_reason,
        job.remarks,
        job.create_user_name
    )

    # job_platform
    if job_platform:
        task_query = task.select(task.job_uuid.distinct()).where(
            task.platform_code.in_(job_platform)).alias('job_temp')
        query = query.join(task_query, JOIN.RIGHT_OUTER, on=(task_query.c.job_uuid == job.job_uuid),
                           attr='job_temp')

    # 筛选已填参数
    # job_name
    query = query.where(job.job_name.contains(job_name)) if job_name else query
    # job_status
    query = query.where(job.job_status.in_(job_status)) if job_status else query
    # create_user_name
    query = query.where(
        job.create_user_name.contains(create_user_name)) if create_user_name else query

    total_num = query.count()
    # 分页排序
    query = query.order_by(
        job.id.desc()
    ).paginate(page_size, page_offset)

    result = {
        'jobList': [{
            'jobUuid': i.job_uuid,
            'jobCode': i.job_code,
            'jobPlatforms': '、'.join(list(map(lambda x: platform_code_zh[int(x)], list(
                set('/'.join([i['platform'] for i in eval(i.job_desc).get('job_content')]).split('/')))))),
            'jobName': i.job_name,
            'jobLimitNum': sum(
                len(i.get('platform').split('/')) * len(i.get('keywords').split('/')) * i.get('limitnum') for i in
                eval(i.job_desc).get('job_content')),
            'jobStartTime': DateTimeHelper.format_datetime(
                DateTimeHelper.parse_formatted_datetime(
                    str(eval(i.job_desc).get('job_content')[0].get('starttime')
                        ), '%Y%m%d'
                ), '%Y.%m.%d'),
            'jobEndTime': DateTimeHelper.format_datetime(
                DateTimeHelper.parse_formatted_datetime(
                    str(eval(i.job_desc).get('job_content')[0].get('endtime')
                        ), '%Y%m%d'
                ), '%Y.%m.%d'),
            'jobStatus': status_code[i.job_status],
            'cancelReason': i.cancel_reason,
            'remarks': i.remarks,
            'CreateUserName': i.create_user_name,
            'CreateTime': str(i.job_created_time)
        } for i in query],
        'totalItems': total_num,  # 当前搜索结果下总数据量
        'totalPages': int(total_num / 10) + 1  # 当前搜索结果下总页数
    }

    return RespOkModel(
        data=result
    )


@app.post('/dts-auto-brief/job/view_article_list')
async def view_article_list(
        stage_uuid: str = Query(...),
        post_min_time: str = Query(None),
        post_max_time: str = Query(None),
        article_type: int = Query(None),  # 0: 直发  1: 转发
        sort_type: int = Query(default=-1),  # # 默认降序
        sort_value: int = Query(default=1),  # 默认发文时间
        page_offset: int = Query(default=50),
        page_size: int = Query(default=1),
        platform: int = Query(...),
        user_name: str = Query(None),  # 用户昵称
        note_title: str = Query(None),  # 文章标题
        user_level: int = Query(None),  # 账号级别
        min_likes: int = Query(None),  # 最小点赞量
        max_likes: int = Query(None),  # 最大点赞量
        min_comments: int = Query(None),  # 最小评论量
        max_comments: int = Query(None),  # 最大评论量
        min_colls: int = Query(None),  # 最小收藏量
        max_colls: int = Query(None),  # 最大收藏量
        min_shares: int = Query(None),  # 最小分享量
        max_shares: int = Query(None),  # 最大分享量
        min_reads: int = Query(None),  # 最小阅读数
        max_reads: int = Query(None),  # 最大阅读数
        min_plays: int = Query(None),  # 最小播放量
        max_plays: int = Query(None),  # 最大播放量
        min_danmus: int = Query(None),  # 最小弹幕数
        max_danmus: int = Query(None),  # 最大弹幕数
        min_downloads: int = Query(None),  # 最小下载数
        max_downloads: int = Query(None),  # 最大下载数
        min_interaction: int = Query(None),  # 最大互动量
        max_interaction: int = Query(None),  # 最大互动量
        min_interaction_per: float = Query(None),  # 最大互动率
        max_interaction_per: float = Query(None),  # 最大互动率
):
    """
    查看文章list
    :param stage_uuid:
    :param post_min_time:
    :param post_max_time:
    :param article_type:
    :param sort_type:
    :param sort_value:
    :param page_offset:
    :param page_size:
    :param platform:
    :param user_name:
    :param note_title:
    :param user_level:
    :param min_likes:
    :param max_likes:
    :param min_comments:
    :param max_comments:
    :param min_colls:
    :param max_colls:
    :param min_shares:
    :param max_shares:
    :param min_reads:
    :param max_reads:
    :param min_plays:
    :param max_plays:
    :param min_danmus:
    :param max_danmus:
    :param min_downloads:
    :param max_downloads:
    :param min_interaction:
    :param max_interaction:
    :param min_interaction_per:
    :param max_interaction_per:
    :return:
    """
    def scope_query_func(x, y, z, k):
        # query = query.where(wx.read_num >= min_reads) if min_reads else query
        # query = query.where(wx.read_num <= max_reads) if max_reads else query
        # 匿名函数 代替上述2个过滤最大最小值的查询
        # scope_query_func = lambda x, y, z, k: x.where(y >= z) if z else x.where(y <= k) if k else x
        return x.where(y >= z) if z else x.where(y <= k) if k else x

    def sort_query_func(x, y, z, j, k):
        # sort_type_tmp = sort_value_tmp_dict[sort_value].desc() if sort_type == -1 else sort_value_tmp_dict[
        #             sort_value].asc()
        # query = query.order_by(sort_type_tmp).paginate(page_size, page_offset)
        # sort_query_func = lambda x, y, z, j, k: x.order_by(y.desc() if z == -1 else y.asc()).paginate(j, k)
        return x.order_by(y.desc() if z == -1 else y.asc()).paginate(j, k)

    if platform == 1:
        # 微信
        sort_dict = {
            1: wx.post_time,  # 发文时间
            2: wx.like,  # 点赞量
            3: wx.read,  # 阅读量
            4: wx.interaction  # 互动
        }
        query = wx.select(
            wx.url,
            wx.title,
            wx.post_time,
            wx.read,
            wx.like,
            wx.interaction,
            wx.user_name,
            wx.user_fans
        )
        # 这里只是为了让代码简洁一点
        query = scope_query_func(query, wx.read, min_reads, max_reads)
        query = scope_query_func(query, wx.like, min_likes, max_likes)
        query = query.where(wx.title.contains(note_title)) if note_title else query
    elif platform == 2:
        # 微博
        sort_dict = {
            1: wb.post_time,  # 发文时间
            2: wb.share,  # 转发(分享)量
            3: wb.comment,  # 评论量
            4: wb.like,  # 点赞数
            5: wb.interaction  # 互动
        }
        query = wb.select(
            wb.url,
            wb.content,
            wb.post_time,
            wb.share,
            wb.comment,
            wb.like,
            wb.interaction,
            wb.user_name,
            wb.user_fans
        )
        query = scope_query_func(query, wb.share, min_shares, max_shares)
        query = scope_query_func(query, wb.comment, min_comments, max_comments)
        query = scope_query_func(query, wb.like, min_likes, max_likes)
        query = query.where(wb.content.contains(note_title)) if note_title else query
    elif platform == 3:
        # 小红书
        sort_dict = {
            1: rb.post_time,  # 发文时间
            2: rb.share,  # 总分享量
            3: rb.comment,  # 总评论量
            4: rb.like,  # 总点赞数
            5: rb.collect,  # 总收藏量
            6: rb.note_collect_like_num,  # 总获赞或收藏量
            7: rb.interaction,  # 文章总互动
            8: rb.interaction_per,  # 文章互动率
        }
        query = rb.select(
            rb.url,
            rb.title,
            rb.note_type,
            rb.post_time,
            rb.like,
            rb.comment,
            rb.collect,
            rb.share,
            rb.interaction,
            rb.interaction_per,
            rb.user_name,
            rb.user_fans,
            rb.user_fans_level,
        )
        query = scope_query_func(query, rb.share, min_shares, max_shares)
        query = scope_query_func(query, rb.comment, min_comments, max_comments)
        query = scope_query_func(query, rb.like, min_likes, max_likes)
        query = scope_query_func(query, rb.collect, min_colls, max_colls)

        # TODO article_type == 1:  # 图文 article_type == 2:  # 视频
        article_type_dict = {1: '图文', 2: 'video'}
        query = query.where(rb.note_type == article_type_dict[article_type]) if article_type else query

        user_dict = {1: '头部kol', 2: '腰部kol', 3: '底部kol', 4: '素人', }
        query = query.where(rb.user_fans_level == user_dict[user_level]) if user_level else query

        query = query.where(rb.title.contains(note_title)) if note_title else query
        query = scope_query_func(query, rb.interaction, min_interaction_per, max_interaction_per)
    elif platform == 4:
        # B站
        sort_dict = {
            1: bi.post_time,  # 发文时间
            2: bi.play,  # 总播放量
            3: bi.danmu,  # 总弹幕量
            4: bi.collect,  # 总收藏数
            5: bi.comment,  # 总评论量
            6: bi.interaction,  # 互动
        }
        query = bi.select(
            bi.url,
            bi.title,
            bi.post_time,
            bi.play,
            bi.danmu,
            bi.collect,
            bi.comment,
            bi.interaction,
            bi.user_name,
            bi.user_fans
        )
        query = scope_query_func(query, bi.play, min_plays, max_plays)
        query = scope_query_func(query, bi.comment, min_comments, max_comments)
        query = scope_query_func(query, bi.danmu, min_danmus, max_danmus)
        query = scope_query_func(query, bi.collect, min_colls, max_colls)
        query = query.where(bi.title.contains(note_title)) if note_title else query
    elif platform == 5:
        # 抖音
        sort_dict = {
            1: dy.post_time,  # 发文时间
            2: dy.like,  # 点赞量
            3: dy.comment,  # 评论量
            4: dy.share,  # 转发量
            5: dy.download,  # 下载量
            6: dy.interaction  # 互动
        }
        query = dy.select(
            dy.url,
            dy.title,
            dy.post_time,
            dy.like,
            dy.comment,
            dy.share,
            dy.download,
            dy.interaction,
            dy.user_name,
            dy.user_fans
        )
        query = scope_query_func(query, dy.like, min_likes, max_likes)
        query = scope_query_func(query, dy.comment, min_comments, max_comments)
        query = scope_query_func(query, dy.share, min_shares, max_shares)
        query = scope_query_func(query, dy.download, min_downloads, max_downloads)
        query = query.where(dy.title.contains(note_title)) if note_title else query
    else:
        return RespErrModel(
            data={'msg': 'platform is invaild'}
        )

    # common 筛选条件
    query = query.where(platform_code_query[platform].user_name.contains(user_name)) if user_name else query
    query = scope_query_func(query, platform_code_query[platform].post_time, post_min_time, post_max_time)
    query = scope_query_func(query, platform_code_query[platform].interaction, min_interaction, max_interaction)

    query = query.where(platform_code_query[platform].stage_uuid == stage_uuid)
    total_num = query.count()

    # 排序获取分页结果
    query = sort_query_func(query, sort_dict[sort_value], sort_type, page_size, page_offset)

    # replace_field_func = lambda x, y: dict(zip(list(y[0]), [x[i] if i != 'post_time' else str(x[i]) for i in y[1]]))
    def replace_field_func(x, y):
        return dict(zip(list(y[0]), [x[i] if i != 'post_time' else str(x[i]) for i in y[1]]))

    result = {
        'data': list(
            map(lambda x: replace_field_func(x.__data__, platform_code_view_field_replace[platform]), list(query))),
        'pageSize': page_size,
        'totalNum': total_num
    }
    result = {
        'err_code': 0,
        'err_msg': 'job view successfully.',
        'data': result
    }

    return RespOkModel(
        data=result
    )


@app.post('/dts-auto-brief/job/view_account_list')
async def view_account_list(
        stage_uuid: str = Query(...),
        account_name: str = Query(""),
        account_min_fans: int = Query(0),
        account_max_fans: int = Query(None),
        page_offset: int = Query(default=50),
        page_size: int = Query(default=1),
        platform: int = Query(...),
        kol_level: List[int] = Query(None)
):
    """
    查看账号list
    :param stage_uuid:
    :param account_name:
    :param account_min_fans:
    :param account_max_fans:
    :param page_offset:
    :param page_size:
    :param platform:
    :param kol_level:
    :return:
    """
    # params: stage_uuid, account_name, account_min_fans,account_max_fans
    # 打印params
    logger.info('requests_params: '
                f'stage_uuid: {stage_uuid}, '
                f'account_name:{account_name},'
                f'account_min_fans:{account_min_fans},'
                f'account_max_fans:{account_max_fans}，'
                f'page_offset：{page_offset},'
                f'page_size：{page_size},'
                f'platform：{platform},'
                f'kol_level：{kol_level}')

    # scope_query_func = lambda x, y, z, k: x.where(y >= z) if z else x.where(y <= k) if k else x
    def scope_query_func(x, y, z, k):
        return x.where(y >= z) if z else x.where(y <= k) if k else x

    if platform == 1:
        # 查询 50个账号出来
        query1 = wx.select(
            wx.user_name,
            fn.SUM(wx.read).alias('sumRead'),
            fn.SUM(wx.like).alias('sumLike'),
            fn.COUNT(wx.id).alias('sumNum'),
        ).group_by(wx.user_name)

        query1 = query1.where(wx.stage_uuid == stage_uuid)

        query1 = scope_query_func(query1, wx.user_fans, account_min_fans, account_max_fans)
        query1 = query1.where(wx.user_name.contains(account_name)) if account_name else query1

        total_num = query1.count()
        query1 = query1.paginate(page_size, page_offset).alias('temp')
        query = wx.select(
            wx.user_name,
            wx.url,
            wx.title,
            wx.read,
            wx.like,
            wx.post_time,
            query1.c.sumRead,
            query1.c.sumLike,
            query1.c.sumNum
        ).join(query1, JOIN.LEFT_OUTER, on=(query1.c.user_name == wx.user_name), attr='temp').where(
            query1.c.sumNum.is_null(False))
        data = dict(zip([i.user_name for i in query1], [{
            'articleList': [],
            "fansNum": 0,
            "sumLike": int(i.sumLike),
            "sumNum": int(i.sumNum),
            "sumRead": int(i.sumRead),
            "userName": i.user_name
        } for i in query1]))

        for i in query:
            data[i.user_name]['articleList'].append({
                'article_url': i.url,
                'title': i.title,
                'read_num': i.read,
                'like_num': i.like,
                'post_time': i.post_time
            })
    elif platform == 2:
        query1 = wb.select(
            wb.user_name,
            wb.user_fans,
            fn.SUM(wb.comment).alias('sumComment'),
            fn.SUM(wb.like).alias('sumLike'),
            fn.SUM(wb.share).alias('sumRepost'),
            fn.COUNT(wb.id).alias('sumNum'),
        ).group_by(wb.user_name)

        query1 = query1.where(wb.stage_uuid == stage_uuid)

        query1 = scope_query_func(query1, wb.user_fans, account_min_fans, account_max_fans)
        query1 = query1.where(wb.user_name.contains(account_name)) if account_name else query1

        total_num = query1.count()
        query1 = query1.paginate(page_size, page_offset).alias('temp')
        query = wb.select(
            wb.user_name,
            wb.url,
            wb.content,
            wb.is_repost,
            wb.share,
            wb.comment,
            wb.like,
            wb.post_time,
            query1.c.sumComment,
            query1.c.sumLike,
            query1.c.sumRepost,
            query1.c.sumNum
        ).join(query1, JOIN.LEFT_OUTER, on=(query1.c.user_name == wb.user_name), attr='temp').where(
            query1.c.sumNum.is_null(False))
        data = dict(zip([i.user_name for i in query1], [{
            'articleList': [],
            "fansNum": i.user_fans,
            "sumLike": int(i.sumLike),
            "sumNum": int(i.sumNum),
            "sumRepost": int(i.sumRepost),
            "sumComment": int(i.sumComment),
            "userName": i.user_name
        } for i in query1]))

        for i in query:
            data[i.user_name]['articleList'].append({
                'article_url': i.url,
                'content': i.content,
                'is_repost': i.is_repost,
                'repost': i.share,
                'like': i.like,
                'comment': i.comment,
                'post_time': i.post_time
            })
    elif platform == 3:
        query1 = rb.select(
            rb.user_name,
            rb.user_fans,
            rb.user_fans_level,
            fn.SUM(rb.collect).alias('sumCollect'),
            fn.SUM(rb.comment).alias('sumComment'),
            fn.SUM(rb.like).alias('sumLike'),
            fn.SUM(rb.share).alias('sumShare'),
            fn.COUNT(rb.id).alias('sumNum'),
        ).group_by(rb.user_name)

        query1 = query1.where(rb.stage_uuid == stage_uuid)

        query1 = scope_query_func(query1, rb.user_fans, account_min_fans, account_max_fans)
        user_dict = {
            1: '头部kol',
            2: '腰部kol',
            3: '底部kol',
            4: '素人',
        }
        query1 = query1.where(rb.user_fans_level.in_([user_dict[i] for i in kol_level])) if kol_level else query1

        total_num = query1.count()
        query1 = query1.paginate(page_size, page_offset).alias('temp')

        query = rb.select(
            rb.user_name,
            rb.url,
            rb.title,
            rb.like,
            rb.comment,
            rb.collect,
            rb.share,
            rb.post_time,
            query1.c.sumCollect,
            query1.c.sumComment,
            query1.c.sumLike,
            query1.c.sumShare,
            query1.c.sumNum
        ).join(query1, JOIN.LEFT_OUTER, on=(query1.c.user_name == rb.user_name), attr='temp').where(
            query1.c.sumNum.is_null(False))

        data = dict(zip([i.user_name for i in query1], [{
            'articleList': [],
            "fansNum": i.user_fans,
            "sumCollect": int(i.sumCollect),
            "sumComment": int(i.sumComment),
            "sumLike": int(i.sumLike),
            "sumShare": int(i.sumShare),
            "sumNum": int(i.sumNum),
            "userName": i.user_name
        } for i in query1]))

        for i in query:
            data[i.user_name]['articleList'].append({
                'note_url': i.url,
                'note_title': i.title,
                'note_like_num': i.like,
                'note_comment_num': i.comment,
                'note_collect_num': i.collect,
                'note_share_num': i.share,
                'note_post_time': i.post_time
            })
    elif platform == 4:
        query1 = bi.select(
            bi.user_name,
            bi.user_fans,
            fn.SUM(bi.danmu).alias('sumBarrage'),
            fn.SUM(bi.collect).alias('sumCollect'),
            fn.SUM(bi.comment).alias('sumComment'),
            fn.SUM(bi.play).alias('sumPlay'),
            fn.COUNT(bi.id).alias('sumNum'),
        ).group_by(bi.user_name)

        query1 = query1.where(bi.stage_uuid == stage_uuid)

        query1 = scope_query_func(query1, bi.user_fans, account_min_fans, account_max_fans)
        query1 = query1.where(bi.user_name.contains(account_name)) if account_name else query1

        total_num = query1.count()
        query1 = query1.paginate(page_size, page_offset).alias('temp')

        query = bi.select(
            bi.user_name,
            bi.url,
            bi.title,
            bi.play,
            bi.comment,
            bi.collect,
            bi.danmu,
            bi.post_time,
            query1.c.sumBarrage,
            query1.c.sumCollect,
            query1.c.sumComment,
            query1.c.sumPlay,
            query1.c.sumNum
        ).join(query1, JOIN.LEFT_OUTER, on=(query1.c.user_name == bi.user_name), attr='temp').where(
            query1.c.sumNum.is_null(False))
        data = dict(zip([i.user_name for i in query1], [{
            'articleList': [],
            "fansNum": i.user_fans,
            "sumCollect": int(i.sumCollect),
            "sumComment": int(i.sumComment),
            "sumBarrage": int(i.sumBarrage),
            "sumPlay": int(i.sumPlay),
            "sumNum": int(i.sumNum),
            "userName": i.user_name
        } for i in query1]))
        for i in query:
            data[i.user_name]['articleList'].append({
                'arcurl': i.url,
                'title': i.title,
                'play': i.play,
                'video_review': i.danmu,
                'favorites': i.collect,
                'review': i.comment,
                'post_time': i.post_time
            })
    elif platform == 5:
        query1 = dy.select(
            dy.user_name,
            dy.user_fans,
            fn.SUM(dy.download).alias('sumDownload'),
            fn.SUM(dy.comment).alias('sumComment'),
            fn.SUM(dy.forward).alias('sumLike'),
            fn.SUM(dy.share).alias('sumForward'),
            fn.COUNT(dy.id).alias('sumNum'),
        ).group_by(dy.user_name)

        query1 = query1.where(dy.stage_uuid == stage_uuid)

        query1 = scope_query_func(query1, dy.user_fans, account_min_fans, account_max_fans)
        query1 = query1.where(dy.user_name.contains(account_name)) if account_name else query1

        total_num = query1.count()
        query1 = query1.paginate(page_size, page_offset).alias('temp')
        query = dy.select(
            dy.user_name,
            dy.url,
            dy.title,
            dy.like,
            dy.comment,
            dy.download,
            dy.forward,
            dy.post_time,
            query1.c.sumDownload,
            query1.c.sumComment,
            query1.c.sumLike,
            query1.c.sumForward,
            query1.c.sumNum
        ).join(query1, JOIN.LEFT_OUTER, on=(query1.c.user_name == dy.user_name), attr='temp').where(
            query1.c.sumNum.is_null(False))
        data = dict(zip([i.user_name for i in query1], [{
            'articleList': [],
            "fansNum": i.user_fans,
            "sumDownload": int(i.sumDownload),
            "sumComment": int(i.sumComment),
            "sumLike": int(i.sumLike),
            "sumForward": int(i.sumForward),
            "sumNum": int(i.sumNum),
            "userName": i.user_name
        } for i in query1]))
        for i in query:
            data[i.user_name]['articleList'].append({
                'content_url': i.url,
                'title': i.title,
                'like_num': i.like,
                'comment_num': i.comment,
                'forward_num': i.forward,
                'download_num': i.download,
                'post_time': i.post_time
            })
    else:
        return RespErrModel(
            data={'msg': 'platform is invaild'}
        )

    result = {'data': list(data.values()), 'pageSize': page_size, 'totalNum': total_num}
    result = {
        'err_code': 0,
        'err_msg': 'job view successfully.',
        'data': result
    }

    return RespOkModel(
        data=result
    )


# 本地文件
@app.get('/dts-auto-brief/download')
async def file_download(
        stage_uuid: str = Query(...),
        file_name: str = Query(...)
):
    """文件下载

    :param file_name:
    :param stage_uuid:
    :return:
    """
    stage_path = f"{system_config['path']}/data/{stage_uuid}"
    if not os.path.exists(f'{stage_path}.zip'):
        _thread.start_new_thread(JobServer.export_stage, (stage_uuid, 2,))
        return "报告正在生成中，请1-2分钟后再次点击尝试"
    # 每次下载都为下次做更新，防止下次导出有问题 Too little data for declared Content-Length
    _thread.start_new_thread(JobServer.export_stage, (stage_uuid, 1,))
    return FileResponse(path=f'{stage_path}.zip',
                        media_type='application/octet-stream',
                        filename=f'{file_name}.zip')


# 本地词云
@app.get('/dts-auto-brief/img')
async def img_show(
        stage_uuid: str = Query(...),
        platform: str = Query(...),
        img_type: str = Query(...)
):
    """
    网络图片流
    :param stage_uuid:
    :param platform:
    :param img_type:
    :return:
    """
    stage_path = f"{system_config['path']}/data/{stage_uuid}"
    file_like = open(f'{stage_path}/wc_{platform}_{img_type}.png', mode="rb")
    return StreamingResponse(file_like, media_type="image/jpg")


# 手动生成zip
@app.get('/dts-auto-brief/zip')
async def img_show(
        job_uuid: str = Query(...)
):
    """
    手动生成zip
    :param job_uuid:
    :return:
    """
    query = stage.select(stage.stage_uuid).where(stage.job_uuid == job_uuid)
    for i in query:
        stage_uuid = i.stage_uuid
        _thread.start_new_thread(JobServer.export_stage, (stage_uuid, 1,))


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8999)
