"""
@version: 1.0
@author: anne
@contact: thy.self@foxmail.com
@time: 2021/12/16 下午5:48
"""
import pymysql

from src.commons.common_job_models_alias import wx, wb, rb, bi, dy
from src.config.main import mysql_config
from src.services.save_service import MysqlSave
from src.services.worker.mweibo_worker import app as mweibo_worker
from src.services.worker.douyin_worker import app as douyin_worker
from src.services.worker.weixin_worker import app as weixin_worker
from src.services.worker.redbook_worker import app as redbook_worker
from src.services.worker.bili_worker import app as bili_worker

# 参数码表

# 平台码 - worker对象
platform_code_worker = {
    1: weixin_worker,
    2: mweibo_worker,
    3: redbook_worker,
    4: bili_worker,
    5: douyin_worker
}

# 平台码 - 中文字符串
platform_code_zh = {
    1: "微信",
    2: "微博",
    3: "小红书",
    4: "B站",
    5: "抖音"
}

# 平台码 - 中文字符串
platform_code_en = {
    1: "weixin",
    2: "weibo",
    3: "redbook",
    4: "bili",
    5: "douyin"
}
# 平台码 - model类别名
platform_code_query = {
    1: wx,
    2: wb,
    3: rb,
    4: bi,
    5: dy
}

# 平台码 - save方法
platform_code_save = {
    1: MysqlSave.save_weixin,
    2: MysqlSave.save_weibo,
    3: MysqlSave.save_redbook,
    4: MysqlSave.save_bili,
    5: MysqlSave.save_douyin
}

# 平台码 - list 一页 文章数
platform_code_pages = {
    1: 10,
    2: 10,
    3: 20,
    4: 20,
    5: 12
}

# 平台码 - view 接口 数据库字段名 - 前端json字段名 映射
platform_code_view_field_replace = {
    1: [
        [
            'article_url',
            'title',
            'post_time',
            'read_num',
            'like_num',
            'note_interaction_sum',
            'weixin_nickname',
            'fans_num'
        ],
        [
            'url',
            'title',
            'post_time',
            'read',
            'like',
            'interaction',
            'user_name',
            'user_fans'
        ]
    ],
    2: [
        [
            'article_url',
            'content',
            'post_time',
            'all_repost',
            'all_comment',
            'all_like',
            'note_interaction_sum',
            'user_name',
            'fans_num'
        ],
        [
            'url',
            'content',
            'post_time',
            'share',
            'comment',
            'like',
            'interaction',
            'user_name',
            'user_fans'
        ]
    ],
    3: [
        [
            'note_url',
            'note_title',
            'note_type',
            'note_post_time',
            'note_like_num',
            'note_comment_num',
            'note_collect_num',
            'note_share_num',
            'note_interaction_sum',
            'note_interaction_per',
            'user_name',
            'user_fans_num',
            'user_fans_level',
        ],
        [
            'url',
            'title',
            'note_type',
            'post_time',
            'like',
            'comment',
            'collect',
            'share',
            'interaction',
            'interaction_per',
            'user_name',
            'user_fans',
            'user_fans_level',
        ]
    ],
    4: [
        [
            'arcurl',
            'title',
            'post_time',
            'play',
            'video_review',
            'favorites',
            'review',
            'note_interaction_sum',
            'author',
            'fans_num'
        ],
        [
            'url',
            'title',
            'post_time',
            'play',
            'danmu',
            'collect',
            'comment',
            'interaction',
            'user_name',
            'user_fans'
        ]
    ],
    5: [
        [
            'content_url',
            'title',
            'post_time',
            'like_num',
            'comment_num',
            'forward_num',
            'download_num',
            'note_interaction_sum',
            'nick_name',
            'user_fans_num'
        ],
        [
            'url',
            'title',
            'post_time',
            'like',
            'comment',
            'share',
            'download',
            'interaction',
            'user_name',
            'user_fans'
        ]
    ]
}

# 平台码 - 词云字段
platform_code_wc_field = {
    1: [[wx.content, wx.content], ['content', 'content']],
    2: [[wb.content, wb.content], ['content', 'content']],
    3: [[rb.content, rb.title], ['content', 'title']],
    4: [[bi.title, bi.tag], ['title', 'tag']],
    5: [[dy.content, dy.content], ['content', 'content']]
}

# 平台码 - 词云所需源数据 df提取标题
platform_code_wc_df_title = {
    1: ['文章内容', '文章标题'],
    2: ['文章内容', '文章内容'],
    3: ['文章内容', '文章标题'],
    4: ['标题', '标签'],
    5: ['文章内容', '文章内容']
}

# 平台码 - excel源数据导出 所有标题
platform_code_excel_df_title = {
    1: ['文章标题', '文章内容', '发布时间', '文章链接', '发布位置', '文章阅读数', '文章点赞数', '文章评论数', '用户名', '用户ID', '粉丝数', '总互动量'],
    2: ['用户链接', '用户id', '用户名', '粉丝数', '关注数', '发布数', '文章链接', '文章内容', '发布时间',
        '文章点赞数', '文章评论数', '文章转发数', '总互动数', '是否直发（0：直发，1：转发） '],
    3: ['用户链接', '用户名', '用户签名', '用户等级', '用户所在区域', '粉丝数', 'kol级别', '获赞数', '关注数', '收藏数', '获赞与收藏数', '笔记数',
        '文章链接', '文章类型', '文章标题', '文章内容', '发布时间', '文章点赞数', '文章评论数', '文章收藏数', '文章分享数', '文章获赞与收藏数',
        '互动率', '评分', '合作品牌', '特征词'],
    4: ['视频类型', '发布类型', '视频链接', '标题', '视频简介', '视频图片链接', '视频播放数', '视频弹幕数', '视频收藏数', '视频评论数', '视频硬币数',
        '视频点赞数',
        '视频分享数', '总互动量', '标签', '视频时长', '发布时间', '用户名', '用户id', '用户链接', '用户关注数', '用户粉丝数'],

    5: ['标题', '文章链接', '文章内容', '视频点赞数', '视频下载数', '视频分享数', '视频关注数', '视频评论数', '发布时间', '用户id',
        '用户名', '用户签名', '用户链接', '粉丝数', '关注数', '点赞数', '总互动数']
}

# pymysql 连接对象
db = 'dts_prod'
pymysql_conn = pymysql.connect(host=mysql_config[db]['host'], port=mysql_config[db]['port'],
                               user=mysql_config[db]['user'],
                               passwd=mysql_config[db]['password'], db=db, use_unicode=True,
                               charset=mysql_config[db]['charset'])

# job 状态 中文字符串， search接口51wom列表页需要中文展示
status_code = {
    0: '准备中',
    1: '执行中',
    2: '已完成',
    3: '已取消',
    4: '执行中',
    5: '审核失败'
}

# 画图和词云的相关配置文件路径
docker_path = '/app/dts-auto-brief-v1'
# docker_path = system_config['path']
simhei = f"{docker_path}/file/simhei.ttf"
ciyun = f"{docker_path}/file/ciyun.jpg"
deng = f"{docker_path}/file/Deng.ttf"
yun = f"{docker_path}/file/yun.jpg"
ball = f"{docker_path}/file/篮球.jpg"
