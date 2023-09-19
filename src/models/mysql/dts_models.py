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

database = 'dts_prod'


info = mysql_config[database]


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass


db = ReconnectMySQLDatabase(host=info['host'], user=info['user'], passwd=info['password'], database=database,
                            charset=info['charset'], port=info['port'])


class BaseModel(Model):
    class Meta:
        database = db


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

    class Meta:
        table_name = 'data_tool_51wom_brief_job'


class FastBriefBiliArticle(BaseModel):
    coin = BigIntegerField(null=True)
    collect = BigIntegerField(null=True)
    comment = BigIntegerField(null=True)
    content = TextField(null=True)
    danmu = BigIntegerField(null=True)
    duration = CharField(null=True)
    id = BigAutoField()
    img_url = CharField(null=True)
    interaction = BigIntegerField(null=True)
    like = BigIntegerField(null=True)
    play = BigIntegerField(null=True)
    post_time = DateTimeField()
    post_type = CharField(null=True)
    share = BigIntegerField(null=True)
    tag = CharField(null=True)
    task_uuid = CharField()
    stage_uuid = CharField()
    title = CharField(null=True)
    url = CharField(null=True)
    user_fans = BigIntegerField(null=True)
    user_follows = BigIntegerField(null=True)
    user_id = CharField(null=True)
    user_name = BigIntegerField(null=True)
    user_url = CharField(null=True)
    video_type = CharField(null=True)
    user_fans_level = CharField(null=True)

    class Meta:
        table_name = 'fast_brief_bili_article'


class FastBriefDouyinArticle(BaseModel):
    comment = BigIntegerField(null=True)
    content = TextField(null=True)
    download = BigIntegerField(null=True)
    forward = BigIntegerField(null=True)
    id = BigAutoField()
    interaction = BigIntegerField(null=True)
    like = BigIntegerField(null=True)
    post_time = DateTimeField()
    share = BigIntegerField(null=True)
    stage_uuid = CharField(null=True)
    task_uuid = CharField()
    title = TextField(null=True)
    url = CharField(null=True)
    user_fans = BigIntegerField(null=True)
    user_follows = BigIntegerField(null=True)
    user_id = BigIntegerField()
    user_likes = BigIntegerField(null=True)
    user_name = CharField()
    user_sign = TextField(null=True)
    user_url = CharField()
    user_fans_level = CharField(null=True)

    class Meta:
        table_name = 'fast_brief_douyin_article'


class FastBriefMweiboArticle(BaseModel):
    comment = BigIntegerField(null=True)
    content = TextField(null=True)
    id = BigAutoField()
    interaction = BigIntegerField(null=True)
    is_repost = IntegerField(null=True)
    like = BigIntegerField(null=True)
    post_time = DateTimeField(null=True)
    share = BigIntegerField(null=True)
    stage_uuid = CharField(null=True)
    task_uuid = CharField(index=True, null=True)
    url = BigIntegerField(null=True)
    user_fans = BigIntegerField(null=True)
    user_follow = BigIntegerField(null=True)
    user_id = BigIntegerField(null=True)
    user_name = CharField(null=True)
    user_post = BigIntegerField(null=True)
    user_fans_level = CharField(null=True)

    class Meta:
        table_name = 'fast_brief_mweibo_article'


class FastBriefRedbookArticle(BaseModel):
    collect = BigIntegerField(null=True)
    comment = BigIntegerField(null=True)
    content = TextField(null=True)
    id = BigAutoField()
    interaction = BigIntegerField(null=True)
    interaction_per = FloatField(null=True)
    like = BigIntegerField(null=True)
    note_collect_like_num = BigIntegerField(null=True)
    note_cooperate_binds = CharField(null=True)
    note_tags = CharField(null=True)
    note_type = CharField(null=True)
    post_time = DateTimeField(null=True)
    score = FloatField(null=True)
    share = BigIntegerField(null=True)
    stage_uuid = CharField(null=True)
    task_uuid = CharField(null=True)
    title = CharField(null=True)
    url = CharField(null=True)
    user_all_note_num = BigIntegerField(null=True)
    user_brief = CharField(null=True)
    user_collect_like_num = BigIntegerField(null=True)
    user_collected_num = BigIntegerField(null=True)
    user_fans = BigIntegerField(null=True)
    user_fans_level = CharField(null=True)
    user_follow_num = BigIntegerField(null=True)
    user_level = CharField(null=True)
    user_like_num = BigIntegerField(null=True)
    user_location = CharField(null=True)
    user_name = CharField(null=True)
    user_url = CharField(null=True)

    class Meta:
        table_name = 'fast_brief_redbook_article'


class FastBriefWeixinArticle(BaseModel):
    article_pos = CharField(null=True)
    comment = BigIntegerField(constraints=[SQL("DEFAULT -1")], null=True)
    content = TextField(null=True)
    id = BigAutoField()
    interaction = BigIntegerField(null=True)
    like = BigIntegerField(null=True)
    post_time = DateTimeField(null=True)
    read = BigIntegerField(null=True)
    stage_uuid = CharField(null=True)
    task_uuid = CharField()
    title = CharField(null=True)
    url = TextField(null=True)
    user_fans = BigIntegerField(null=True)
    user_id = CharField(null=True)
    user_name = CharField(null=True)
    user_fans_level = CharField(null=True)

    class Meta:
        table_name = 'fast_brief_weixin_article'
