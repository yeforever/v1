"""
@version: 1.0
@author: anne
@contact: thy.self@foxmail.com
@time: 2021/12/9 下午2:57
"""
from src.models.mysql.dts_models import FastBriefWeixinArticle, FastBriefMweiboArticle, FastBriefRedbookArticle, \
    FastBriefBiliArticle, FastBriefDouyinArticle, DataTool51WomBriefJob, DataTool51WomBriefTask, DataTool51WomBriefStage

wx = FastBriefWeixinArticle
wb = FastBriefMweiboArticle
rb = FastBriefRedbookArticle
bi = FastBriefBiliArticle
dy = FastBriefDouyinArticle

wx_table = wx()
wb_table = wb()
rb_table = rb()
bi_table = bi()
dy_table = dy()

job = DataTool51WomBriefJob
stage = DataTool51WomBriefStage
task = DataTool51WomBriefTask
