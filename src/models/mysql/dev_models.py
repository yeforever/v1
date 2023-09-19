#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@version: 1.0
@author: guu
@contact: yeexiao@yeah.net
@time: 7/8/17 9:24 PM
"""
from peewee import *
from playhouse.shortcuts import ReconnectMixin

from src.config.main import mysql_config

database = 'dts_dev'


info = mysql_config[database]


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass


# Your db should now automatically attempt to reconnect for certain types of errors.

db = ReconnectMySQLDatabase(host=info['host'], user=info['user'], passwd=info['password'], database=database,
                            charset=info['charset'], port=info['port'])


class BaseModel(Model):
    class Meta:
        database = db


class SocialPublicOpinionJob(BaseModel):
    """ 社交舆情job表
    """

    class Meta:
        table_name = 'social_public_opinion_job'

    @classmethod
    def table_name(cls):
        return 'social_public_opinion_job'

    JOB_TYPE_FIND_ARTICLE = 1  # 找文章
    JOB_TYPE_FIND_ACCOUNT = 2  # 找账号
    JOB_TYPE_FIND_ARTICLE_AND_ACCOUNT = 3  # 找文章&找账号
    JOB_TYPE_OTHER = -1  # 其他
    JOB_TYPE_DICT = {
        JOB_TYPE_FIND_ARTICLE: '找文章',
        JOB_TYPE_FIND_ACCOUNT: '找账号',
        JOB_TYPE_FIND_ARTICLE_AND_ACCOUNT: '找文章&找账号',
        JOB_TYPE_OTHER: '其他'
    }
    PLATFORM_CODE_WEIXIN = 1
    PLATFORM_CODE_WEIBO = 2
    PLATFORM_CODE_XHS = 3
    PLATFORM_CODE_DY = 4
    PLATFORM_CODE_DICT = {
        PLATFORM_CODE_WEIXIN: '微信',
        PLATFORM_CODE_WEIBO: '微博',
        PLATFORM_CODE_XHS: '小红书',
        PLATFORM_CODE_DY: '抖音'
    }
    FROM_TEST = 1  # 测试
    FROM_KMS_SOCIAL_PUBLIC_OPINION = 2
    FROM_51WOM_SOCIAL_PUBLIC_OPINION = 3
    TASK_COME_FROM_DICT = {
        FROM_TEST: '测试',
        FROM_KMS_SOCIAL_PUBLIC_OPINION: 'KMS舆情系统',
        FROM_51WOM_SOCIAL_PUBLIC_OPINION: '51wom找号/找文章功能'
    }
    STATUS_NEW = 1  # JOB新建
    STATUS_CHECK_ENV = 2  # 检测环境
    STATUS_SPIDER = 3  # spider阶段
    STATUS_ETL = 4  # etl阶段
    STATUS_FINISHED = 5  # 完成
    STATUS_ERROR = 6  # 出错
    STATUS_CANCELED = 8  # 取消
    id = AutoField()
    uuid = CharField()
    platform_code = IntegerField()
    name = CharField()
    job_type = SmallIntegerField(default=-1)
    come_from = IntegerField()
    keywords = TextField()
    data_filter = TextField()
    job_status = IntegerField(default=STATUS_NEW)
    total_spider_task = IntegerField()
    finished_spider_task = IntegerField()
    created_at = IntegerField()
    updated_at = IntegerField()


class SocialPublicOpinionSpiderTask(BaseModel):
    """ 社交舆情spider task表
    """

    class Meta:
        table_name = 'social_public_opinion_spider_task'

    @classmethod
    def table_name(cls):
        return 'social_public_opinion_spider_task'

    STATUS_NEW = 1  # 新建
    STATUS_FINISHED = 4  # 采集完成
    STATUS_CANCELED = 8  # 取消
    id = AutoField()
    uuid = CharField()
    job_uuid = CharField()
    group_name = CharField()
    keywords = TextField()
    status = IntegerField(default=STATUS_NEW)
    created_at = IntegerField()
    updated_at = IntegerField()


class SocialPublicOpinionEtlTask(BaseModel):
    """ 社交舆情etl task表
    """

    class Meta:
        table_name = 'social_public_opinion_etl_task'

    @classmethod
    def table_name(cls):
        return 'social_public_opinion_etl_task'

    STATUS_NEW = 1  # 新建
    STATUS_FINISHED = 4  # etl完成
    STATUS_CANCELED = 8  # 取消
    id = AutoField()
    uuid = CharField()
    job_uuid = CharField()
    status = IntegerField(default=STATUS_NEW)
    created_at = IntegerField()
    updated_at = IntegerField()


class SogouWeixinArticleSearchTask(BaseModel):
    """
        搜狗微信文章搜索任务表 sogou_weixin_article_search_task
    """

    class Meta:
        table_name = 'sogou_weixin_article_search_task'

    @classmethod
    def table_name(cls):
        return 'sogou_weixin_article_search_task'

    STATUS_NEW = 1  # 新建
    STATUS_IN_PROGRESS = 2  # 执行中
    STATUS_FAILURE = 3  # 失败
    STATUS_FINISHED = 4  # 完成
    STATUS_CANCELED = 5  # 取消
    STATUS_LABELS = {
        STATUS_NEW: '新建',
        STATUS_IN_PROGRESS: '运行中',
        STATUS_FAILURE: '失败',
        STATUS_FINISHED: '完成',
        STATUS_CANCELED: '取消'
    }
    SPIDER_TYPE_SELENIUM = 1
    SPIDER_TYPE_REQUEST = 2
    SPIDER_TYPE_APP = 3
    SPIDER_TYPE_LABELS = {
        SPIDER_TYPE_SELENIUM: 'selenium采集',
        SPIDER_TYPE_REQUEST: 'request采集',
        SPIDER_TYPE_APP: '微信app采集'
    }
    id = AutoField()
    uuid = CharField(unique=True, max_length=45)
    come_from = SmallIntegerField()
    keywords = CharField(max_length=256)
    start_date = DateTimeField(default='2000-01-01 00:00:00')
    end_date = DateTimeField(default='2030-01-01 00:00:00')
    read_num_limit = IntegerField(default=-1)
    exclude_accounts = TextField()
    spider_type = SmallIntegerField()
    status = SmallIntegerField(default=STATUS_NEW)
    created_at = DateTimeField()
    updated_at = DateTimeField()


class WeixinAppSpiderTask(BaseModel):
    """
        微信APP采集任务表
    """

    class Meta:
        table_name = 'weixin_app_spider_task'

    @classmethod
    def table_name(cls):
        return 'weixin_app_spider_task'

    TASK_TYPE_WEIXIN_ARTICLE_MONITOR = 1  # 微信文章监控
    TASK_TYPE_WEIXIN_ACCOUNT_MONITOR = 2  # 微信账号监控
    TASK_TYPE_WEIXIN_ARTICLE_CRAWLING = 3  # 微信单篇历史文章采集
    TASK_TYPE_SOGOU_WEIXIN_ARTICLE_SEARCH = 4  # 搜狗微信文章搜索
    TASK_TYPE_SOGOU_WEIXIN_ACCOUNT_SEARCH = 5  # 搜狗微信账号搜索
    STATUS_NEW = 0
    STATUS_ASSIGNED = 1
    STATUS_OK = 2
    STATUS_CANCELED = 3
    STATUS_FAIL = 4
    STATUS_LABELS = {
        STATUS_NEW: '新建',
        STATUS_ASSIGNED: '已分配',
        STATUS_OK: '采集成功',
        STATUS_CANCELED: '取消',
        STATUS_FAIL: '失败'
    }
    id = AutoField()
    uuid = CharField(unique=True, max_length=45)
    type = SmallIntegerField()
    global_task_uuid = CharField(max_length=45)
    status = SmallIntegerField(default=STATUS_NEW)
    url = TextField()
    worker_id = IntegerField()
    created_at = IntegerField()
    assign_at = IntegerField()
    finish_at = IntegerField()


class WeixinAppSpiderWorker(BaseModel):
    """
        微信APP采集worker表
    """

    class Meta:
        table_name = 'weixin_app_spider_worker'

    @classmethod
    def table_name(cls):
        return 'weixin_app_spider_worker'

    STATUS_INACTIVE = 0  # 无效
    STATUS_ACTIVE = 1  # 正常
    STATUS_ASLEEP = 2  # 休眠
    id = AutoField()
    openid = CharField()
    name = CharField()
    avatar = CharField()
    mobile = IntegerField()
    weixin_id = CharField()
    accept_tasks = CharField()
    latest_heart_beat = IntegerField()
    comment = TextField()
    status = SmallIntegerField()
    created_at = IntegerField()
    updated_at = IntegerField()


class WeiboSpiderAccount(BaseModel):
    """
        微博爬虫账号
    """

    class Meta:
        table_name = 'weibo_spider_account'

    @classmethod
    def table_name(cls):
        return 'weibo_spider_account'

    id = AutoField()
    username = TextField()
    password = TextField()
    cookies = TextField()
    created_at = TextField()
    ip = TextField()
    status = IntegerField()


class MediaWeixin(BaseModel):
    """
        微信账号表
    """

    class Meta:
        table_name = 'media_weixin'

    @classmethod
    def table_name(cls):
        return 'media_weixin'

    STATUS_VALID = 1
    STATUS_INVALID = 0
    SPIDER_TYPE_DW = 1
    SPIDER_TYPE_WEIXIN_APP = 2
    id = AutoField()
    weixin_id = CharField(unique=True)
    weixin_name = CharField()
    account_biz_code = CharField(null=True)
    account_desc = CharField(null=True)
    account_ownership = CharField(null=True)
    is_auth = IntegerField(default=-1)
    follower_num = IntegerField(default=-1)
    price_info = TextField(null=True)
    media_areas = CharField(null=True)
    media_cates = CharField(null=True)
    wmi = FloatField(default=0.00)
    head_avg_like_num = IntegerField(default=0)
    head_avg_read_num = IntegerField(default=0)
    latest_article_title = CharField()
    latest_post_time = IntegerField()
    latest_article_url = CharField()
    open_comments = SmallIntegerField(default=-1)
    spider_type = SmallIntegerField(default=SPIDER_TYPE_DW)
    status = IntegerField(default=STATUS_VALID)
    comments = CharField(null=True)
    status_sync_dts_media_weixin = SmallIntegerField(default=0)
    status_article_daily_crawling = SmallIntegerField(default=0)
    status_remove_duplicated_articles = SmallIntegerField(default=0)
    status_pre_process_rank_index = SmallIntegerField(default=0)
    status_pre_process_media_list = SmallIntegerField(default=0)
    status_update_dts_rank_list = SmallIntegerField(default=0)
    status_process_dts_rank_score = SmallIntegerField(default=0)
    status_update_dts_media_list = SmallIntegerField(default=0)
    status_migrate_kms_rank_list = SmallIntegerField(default=0)
    status_migrate_kms_media_list = SmallIntegerField(default=0)
    status_migrate_wom_media_list = SmallIntegerField(default=0)
    status_migrate_womdata_rank_list = SmallIntegerField(default=0)
    created_at = IntegerField()
    updated_at = IntegerField()


class XhsTask(BaseModel):
    """
        微信账号表
    """

    class Meta:
        table_name = 'xhs_task'

    @classmethod
    def table_name(cls):
        return 'xhs_task'

    id = AutoField()
    job_uuid = CharField()
    task_uuid = CharField()
    keyword = TextField()
    status = IntegerField()
    create_time = IntegerField()


class XhsCookies(BaseModel):
    """
        小红书cookies表
    """

    class Meta:
        table_name = 'xhs_cookies'

    @classmethod
    def table_name(cls):
        return 'xhs_cookies'

    id = AutoField()
    cookies = TextField()
    at = TextField()
    status = IntegerField()
    updated_time = TextField()


class WeixinCookiesPool(BaseModel):
    """
    微信cookies池
    """

    class Meta:
        table_name = 'weixin_cookies_pool'

    @classmethod
    def table_name(cls):
        return 'weixin_cookies_pool'

    id = AutoField()
    wx_name = CharField()
    cookies = TextField()


class BriefTask(BaseModel):
    """
    工单任务表
    """

    class Meta:
        table_name = 'brief_task'

    @classmethod
    def table_name(cls):
        return 'brief_task'

    STATUS_SLEEP = 0  # 等待中
    STATUS_RUN = 1  # 执行中
    STATUS_FINISHED = 2  # 已完成
    STATUS_CANCELED = 3  # 已取消
    STATUS_ERROR = 4  # 出错
    id = AutoField()
    bilibili_keywords = TextField(null=True)
    bilibili_status = IntegerField(null=True, default=STATUS_SLEEP)
    weixin_status = IntegerField(null=True, default=STATUS_SLEEP)
    redbook_status = IntegerField(null=True, default=STATUS_SLEEP)
    mweibo_status = IntegerField(null=True, default=STATUS_SLEEP)
    data_sum = IntegerField(null=True)
    download_url = TextField(null=True)
    end_time = IntegerField(null=True)
    mweibo_keywords = TextField(null=True)
    redbook_keywords = TextField(null=True)
    start_time = IntegerField(null=True)
    status = IntegerField(null=True, default=STATUS_SLEEP)
    task_uuid = CharField(null=True)
    weixin_keywords = TextField(null=True)


class Mlx_BriefTask(BaseModel):
    """
    工单任务表
    """

    class Meta:
        table_name = 'mlx_brief_task'

    @classmethod
    def table_name(cls):
        return 'mlx_brief_task'

    STATUS_SLEEP = 0  # 等待中
    STATUS_RUN = 1  # 执行中
    STATUS_FINISHED = 2  # 已完成
    STATUS_CANCELED = 3  # 已取消
    STATUS_ERROR = 4  # 出错
    id = AutoField()
    bilibili_keywords = TextField(null=True)
    bilibili_status = IntegerField(null=True, default=STATUS_SLEEP)
    weixin_keywords = TextField(null=True)
    weixin_status = IntegerField(null=True, default=STATUS_SLEEP)
    redbook_keywords = TextField(null=True)
    redbook_status = IntegerField(null=True, default=STATUS_SLEEP)
    mweibo_keywords = TextField(null=True)
    mweibo_status = IntegerField(null=True, default=STATUS_SLEEP)
    weibo_cn_keywords = TextField(null=True)
    weibo_cn_status = IntegerField(null=True, default=STATUS_SLEEP)
    weibo_com_keywords = TextField(null=True)
    weibo_com_status = IntegerField(null=True, default=STATUS_SLEEP)
    data_sum = IntegerField(null=True)
    download_url = TextField(null=True)
    end_time = IntegerField(null=True)
    start_time = IntegerField(null=True)
    reset_status = IntegerField(null=True, default=STATUS_SLEEP)
    article_start_time = DateTimeField(null=True)
    article_end_time = DateTimeField(null=True)
    status = IntegerField(null=True, default=STATUS_SLEEP)
    task_uuid = CharField(null=True)


class AutoBriefJob(BaseModel):
    limit = TextField(null=True)
    id = BigAutoField()
    job_cancel_time = DateTimeField(null=True)
    job_created_time = DateTimeField(null=True)
    job_desc = TextField(null=True)
    job_finish_time = DateTimeField(null=True)
    job_name = CharField(null=True)
    job_run_time = DateTimeField(null=True)
    job_status = IntegerField(null=True)
    job_uuid = CharField(null=True)
    download_url = TextField(null=True)

    class Meta:
        table_name = 'auto_brief_job'

    @classmethod
    def table_name(cls):
        return 'auto_brief_job'


class AutoBriefJobAnalysis(BaseModel):
    article_num_analysis = TextField(null=True)
    avg_article_time = IntegerField(null=True)
    avg_task_time = IntegerField(null=True)
    err_num_analysis = TextField(null=True)
    id = BigAutoField()
    job_uuid = CharField(null=True)
    runtime_analysis = TextField(null=True)
    sum_article_num = IntegerField(null=True)
    sum_err_num = IntegerField(null=True)
    sum_export_article_num = IntegerField(null=True)
    sum_export_file_num = IntegerField(null=True)
    sum_runtime = IntegerField(null=True)
    sum_task_num = IntegerField(null=True)
    task_num_analysis = TextField(null=True)

    class Meta:
        table_name = 'auto_brief_job_analysis'

    @classmethod
    def table_name(cls):
        return 'auto_brief_job_analysis'


class AutoBriefTask(BaseModel):
    id = BigAutoField()
    job_uuid = CharField(null=True)
    platform_code = IntegerField(null=True)
    sum_task_runtime = IntegerField(null=True)
    sum_task_num = IntegerField(null=True)
    task_desc = TextField(null=True)
    task_keyword = CharField(null=True)
    task_limit_endtime = DateTimeField(null=True)
    task_limit_num = IntegerField(null=True)
    task_limit_starttime = DateTimeField(null=True)
    task_run_endtime = DateTimeField(null=True)
    task_run_starttime = DateTimeField(null=True)
    task_status = IntegerField(null=True)
    task_uuid = CharField(null=True)

    class Meta:
        table_name = 'auto_brief_task'

    @classmethod
    def table_name(cls):
        return 'auto_brief_task'


class AutoBriefTaskErrLog(BaseModel):
    err_code = IntegerField(null=True)
    err_msg = TextField(null=True)
    id = BigAutoField()
    job_uuid = CharField(null=True)
    task_uuid = CharField(null=True)

    class Meta:
        table_name = 'auto_brief_task_err_log'

    @classmethod
    def table_name(cls):
        return 'auto_brief_task_err_log'


class Dts51WomRedbookSpiderAuth(BaseModel):
    auth = CharField(null=True)
    id = BigAutoField()

    class Meta:
        table_name = 'dts_51wom_redbook_spider_auth'

    @classmethod
    def table_name(cls):
        return 'dts_51wom_redbook_spider_auth'


class DataTool51WomBriefStage(BaseModel):
    download_url = TextField(null=True)
    id = BigAutoField()
    job_uuid = CharField(null=True)
    stage_created_time = DateTimeField(null=True)
    stage_desc = TextField(null=True)
    stage_finish_time = DateTimeField(null=True)
    stage_name = CharField(null=True)
    stage_run_time = DateTimeField(null=True)
    stage_cancel_time = DateTimeField(null=True)
    stage_status = IntegerField(null=True)
    stage_uuid = CharField(null=True)

    class Meta:
        table_name = 'data_tool_51wom_brief_stage'


class DataTool51WomBriefStageAnalysis(BaseModel):
    account_sum_num = IntegerField(null=True)
    stage_name = CharField(null=True)
    article_comment_sum_num = IntegerField(null=True)
    article_content_wordcloud = TextField(null=True)
    article_like_sum_num = IntegerField(null=True)
    article_repost_sum_num = IntegerField(null=True)
    article_sum_num = IntegerField(null=True)
    article_topic_wordcloud = TextField(null=True)
    end_time = DateTimeField(null=True)
    id = BigAutoField()
    job_uuid = CharField(null=True)
    keywords = CharField(null=True)
    limit_num = IntegerField(null=True)
    platform_code = IntegerField(null=True)
    stage_uuid = CharField(null=True)
    start_time = DateTimeField(null=True)
    redbook_data_analysis_json = TextField(null=True)
    weibo_data_analysis_json = TextField(null=True)
    bili_data_analysis_json = TextField(null=True)
    weixin_data_analysis_json = TextField(null=True)
    douyin_data_analysis_json = TextField(null=True)

    class Meta:
        table_name = 'data_tool_51wom_brief_stage_analysis'


class DataTool51WomBriefTask(BaseModel):
    id = BigAutoField()
    job_uuid = CharField(null=True)
    stage_uuid = CharField(null=True)
    platform_code = IntegerField(null=True)
    sum_task_num = IntegerField(null=True)
    sum_task_runtime = IntegerField(null=True)
    task_desc = TextField(null=True)
    task_keyword = CharField(null=True)
    task_limit_endtime = DateTimeField(null=True)
    task_limit_num = IntegerField(null=True)
    task_limit_starttime = DateTimeField(null=True)
    task_run_endtime = DateTimeField(null=True)
    task_run_starttime = DateTimeField(null=True)
    task_cancel_time = DateTimeField(null=True)
    task_status = IntegerField(null=True)
    task_uuid = CharField(null=True)

    class Meta:
        table_name = 'data_tool_51wom_brief_task'


class DataTool51WomBriefJob(BaseModel):
    download_url = TextField(null=True)
    id = BigAutoField()
    job_code = CharField(null=True)
    job_cancel_time = DateTimeField(null=True)
    job_created_time = DateTimeField(null=True)
    job_desc = TextField(null=True)
    job_finish_time = DateTimeField(null=True)
    job_name = CharField(null=True)
    job_run_time = DateTimeField(null=True)
    job_status = IntegerField(null=True)
    job_uuid = CharField(null=True)
    limit = TextField(null=True)
    cancel_reason = CharField(null=True)
    create_user_name = CharField(null=True)
    remarks = CharField(null=True)
    job_platform = IntegerField(null=True)

    class Meta:
        table_name = 'data_tool_51wom_brief_job'


class FastBriefWeixinArticle(BaseModel):
    article_pos = CharField(null=True)
    article_url = TextField(null=True)
    comment_num = BigIntegerField(constraints=[SQL("DEFAULT -1")], null=True)
    content = TextField(null=True)
    fans_num = BigIntegerField(null=True)
    id = BigAutoField()
    like_num = BigIntegerField(null=True)
    post_time = DateTimeField(null=True)
    read_num = BigIntegerField(null=True)
    stage_uuid = CharField(null=True)
    task_uuid = CharField()
    title = CharField(null=True)
    total_interaction = BigIntegerField(null=True)
    weixin_id = CharField(null=True)
    weixin_nickname = CharField(null=True)

    class Meta:
        table_name = 'fast_brief_weixin_article'

class FastBriefMweiboArticle(BaseModel):
    comment = BigIntegerField(null=True)
    content = TextField(null=True)
    fans = BigIntegerField(null=True)
    follow = BigIntegerField(null=True)
    id = BigAutoField()
    is_repost = IntegerField(null=True)
    like = BigIntegerField(null=True)
    note_interaction_sum = BigIntegerField(null=True)
    note_id = BigIntegerField(null=True)
    post = BigIntegerField(null=True)
    post_time = DateTimeField(null=True)
    repost = BigIntegerField(null=True)
    stage_uuid = CharField(null=True)
    task_uuid = CharField(index=True, null=True)
    user_id = BigIntegerField(null=True)
    user_name = CharField(null=True)

    class Meta:
        table_name = 'fast_brief_mweibo_article'



class ZhimaHelper(BaseModel):
    """
        微信文章es搜索任务表
    """

    class Meta:
        table_name = 'zhima_helper'

    @classmethod
    def table_name(cls):
        return 'zhima_helper'

    id = AutoField()
    proxy_ip = CharField(max_length=30)
    expires_time_ts = IntegerField()


class BoostUserAgent(BaseModel):
    engine = CharField(null=True)
    popularity = CharField(null=True)
    software = CharField(null=True)
    types = CharField(null=True)
    useragent = CharField(null=True)
    timestamp1 = CharField(null=True)
    timestamp2 = CharField(null=True)

    class Meta:
        table_name = 'boost_user_agent'
