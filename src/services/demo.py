# -*- coding: utf-8 -*-
# @Author  : yezi
# @Time    : 2022/8/16
from src.models.mysql.dts_models import FastBriefWeixinArticle, FastBriefMweiboArticle, FastBriefRedbookArticle, \
    FastBriefBiliArticle, FastBriefDouyinArticle, DataTool51WomBriefJob, DataTool51WomBriefTask, DataTool51WomBriefStage
import json
import os
import re
import time
import uuid
import zipfile
from collections import Counter

import jieba
import openpyxl
import requests
from PIL import Image
from openpyxl.drawing.image import Image as Im
from loguru import logger
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import FontProperties
from openpyxl.styles import Alignment
from pandas.core.frame import DataFrame
import pandas as pd
from peewee import fn
from wordcloud import WordCloud

from src.commons.common_job_models_alias import wx, wb, rb, bi, dy, job, task, stage
from src.commons.common_job_params import platform_code_worker, platform_code_pages, \
    platform_code_query, platform_code_wc_field, platform_code_zh, pymysql_conn, platform_code_excel_df_title, \
    platform_code_wc_df_title, simhei, ciyun, deng, ball, platform_code_en
from src.commons.datatime_helper import DateTimeHelper
from src.config.main import system_config
from src.config.params_local import remove_words_list

# matplotlib.use('Agg') 服务端文件导出出错,加上这句导出不报错
matplotlib.use('Agg')

# pandas 直接通过conn 读取mysql 数据
conn = pymysql_conn

rb = FastBriefRedbookArticle

task_uuid = 'b5296890-cbdb-43ba-abce-7226d884caee'
rb_query = rb.select(
            rb.user_url,
            rb.user_name,
            rb.user_brief,
            rb.user_level,
            rb.user_location,
            rb.user_fans,
            rb.user_fans_level,
            rb.user_like_num,
            rb.user_follow_num,
            rb.user_collected_num,
            rb.user_collect_like_num,
            rb.user_all_note_num,
            rb.url,
            rb.note_type,
            rb.title,
            rb.content,
            rb.post_time,
            rb.like,
            rb.comment,
            rb.collect,
            rb.share,
            rb.note_collect_like_num,
            rb.interaction,
            rb.score,
            rb.note_cooperate_binds,
            rb.note_tags
        ).where(
            rb.task_uuid == task_uuid
        ).group_by(rb.url)

sql_dict = {
            3: str(rb_query)
        }
df = pd.read_sql(sql_dict[3], con=conn)
print(df)
df.columns = platform_code_excel_df_title[3]