"""
@version: 1.0
@author: anne
@contact: thy.self@foxmail.com
@time: 2021/11/27 上午9:48
"""
from src.commons.common_job_models_alias import wb_table, wx_table, rb_table, dy_table, bi_table


class MysqlSave(object):

    @classmethod
    def save_weibo(cls, info, auto_id):
        """
        kafka weibo topic 数据存入 mysql
        :param info: kafka weibo topic 数据
        :param auto_id: 自增主键，因为异步insert, 自增主键会冲突
        :return:
        """
        # bins = [-1, 1000000, 5000000, float("inf")]
        # labels = ['底部kol', '腰部kol', '头部kol']

        user_fans = info['fans']
        if 0 <= user_fans < 1000000:
            user_fans_level = '底部kol'
        elif 1000000 <= user_fans < 5000000:
            user_fans_level = '腰部kol'
        else:
            user_fans_level = '头部kol'

        wb = wb_table
        wb.id = auto_id
        wb.stage_uuid = info['stage_uuid']
        wb.task_uuid = info['task_uuid']
        wb.url = 'https://m.weibo.cn/detail/' + info['note_id']
        wb.post_time = info['post_time']
        wb.content = info['content']
        wb.comment = info['comment']
        wb.is_repost = info['is_repost']
        wb.like = info['like']
        wb.share = info['repost']
        wb.interaction = info['like'] + info['comment'] + info['repost']
        wb.user_fans = info['fans']
        wb.user_follow = info['follow']
        wb.user_id = info['user_id']
        wb.user_name = info['user_name']
        wb.user_post = info['post']
        wb.user_fans_level = user_fans_level
        wb.save(force_insert=True)

    @classmethod
    def save_weixin(cls, info, auto_id):
        """
        kafka weixin topic 数据存入 mysql
        :param info: kafka weixin topic 数据
        :param auto_id: 自增主键，因为异步insert, 自增主键会冲突
        :return:
        """
        # bins = [-1, 300000, 800000, float("inf")]
        # labels = ['底部kol', '腰部kol', '头部kol']

        wx = wx_table
        wx.id = auto_id
        wx.stage_uuid = info['stage_uuid']
        wx.task_uuid = info['task_uuid']
        wx.url = info['article_url']
        wx.title = info['title']
        wx.content = info['content']
        wx.post_time = info['post_time']
        wx.article_pos = info['article_pos']
        wx.comment = info['comment_num']
        wx.like = info['like_num']
        wx.read = info['read_num']
        wx.interaction = info['like_num']
        wx.user_fans = info['fans_num']
        wx.user_id = info['weixin_id']
        wx.user_name = info['weixin_nickname']
        wx.user_fans_level = '底部kol'
        wx.save(force_insert=True)

    @classmethod
    def save_redbook(cls, info, auto_id):
        """
        kafka redbook topic 数据存入 mysql
        :param info: kafka redbook topic 数据
        :param auto_id: 自增主键，因为异步insert, 自增主键会冲突
        :return:
        """
        rb = rb_table
        rb.id = auto_id
        rb.collect = info['note_collect_num']
        rb.comment = info['note_comment_num']
        rb.content = info['note_content']
        rb.interaction = info['note_interaction_sum']
        rb.interaction_per = info['note_interaction_per']
        rb.like = info['note_like_num']
        rb.note_collect_like_num = info['note_collect_like_num']
        rb.note_cooperate_binds = info['note_cooperate_binds']
        rb.note_tags = info['note_tags']
        rb.note_type = info['note_type']
        rb.post_time = info['note_post_time']
        rb.score = info['score']
        rb.share = info['note_share_num']
        rb.stage_uuid = info['stage_uuid']
        rb.task_uuid = info['task_uuid']
        rb.title = info['note_title']
        rb.url = info['note_url']
        rb.user_all_note_num = info['user_all_note_num']
        rb.user_brief = info['user_brief']
        rb.user_collect_like_num = info['user_collect_like_num']
        rb.user_collected_num = info['user_collected_num']
        rb.user_fans = info['user_fans_num']
        rb.user_fans_level = info['user_fans_level']
        rb.user_follow_num = info['user_follow_num']
        rb.user_level = info['user_level']
        rb.user_like_num = info['user_like_num']
        rb.user_location = info['user_location']
        rb.user_name = info['user_name']
        rb.user_url = info['user_url']
        rb.save(force_insert=True)

    @classmethod
    def save_douyin(cls, info, auto_id):
        """
        kafka douyin topic 数据存入 mysql
        :param info: kafka douyin topic 数据
        :param auto_id: 自增主键，因为异步insert, 自增主键会冲突
        :return:
        """
        # bins = [-1, 1000000, 5000000, float("inf")]
        # labels = ['底部kol', '腰部kol', '头部kol']

        user_fans = info['user_fans_num']
        if 0 <= user_fans < 1000000:
            user_fans_level = '底部kol'
        elif 1000000 <= user_fans < 5000000:
            user_fans_level = '腰部kol'
        else:
            user_fans_level = '头部kol'

        dy = dy_table
        dy.id = auto_id
        dy.comment = info['comment_num']
        dy.content = info['content']
        dy.download = info['download_num']
        dy.forward = info['forward_num']
        dy.interaction = info['like_num'] + info['download_num'] + info['forward_num'] + info['comment_num']
        dy.like = info['like_num']
        dy.post_time = info['post_time']
        dy.share = info['share_num']
        dy.stage_uuid = info['stage_uuid']
        dy.task_uuid = info['task_uuid']
        dy.title = info['title']
        dy.url = info['content_url']
        dy.user_fans = info['user_fans_num']
        dy.user_fans_level = user_fans_level
        dy.user_follows = info['user_attention_num']
        dy.user_id = info['sec_uid']
        dy.user_likes = info['user_like_num']
        dy.user_name = info['nick_name']
        dy.user_sign = info['signature']
        dy.user_url = info['user_url']
        dy.save(force_insert=True)

    @classmethod
    def save_bili(cls, info, auto_id):
        """
        kafka bili topic 数据存入 mysql
        :param info: kafka bili topic 数据
        :param auto_id: 自增主键，因为异步insert, 自增主键会冲突
        :return:
        """
        # bins = [-1, 100000, 300000, float('inf')]
        # labels = ['底部kol', '腰部kol', '头部kol']
        user_fans = info['fans_num']
        if 0 <= user_fans < 100000:
            user_fans_level = '底部kol'
        elif 100000 <= user_fans < 300000:
            user_fans_level = '腰部kol'
        else:
            user_fans_level = '头部kol'

        bi = bi_table
        bi.id = auto_id
        bi.coin = info['coin']
        bi.collect = info['favorites']
        bi.comment = info['review']
        bi.content = info['description']
        bi.danmu = info['video_review']
        bi.duration = info['duration']
        bi.img_url = info['pic']
        bi.interaction = info['note_interaction_sum']
        bi.like = info['like']
        bi.play = info['play']
        bi.post_time = info['post_time']
        bi.post_type = info['typename']
        bi.share = info['share']
        bi.tag = info['tag']
        bi.task_uuid = info['task_uuid']
        bi.stage_uuid = info['stage_uuid']
        bi.title = info['title']
        bi.url = info['arcurl']
        bi.user_fans = info['fans_num']
        bi.user_fans_level = user_fans_level
        bi.user_follows = info['attention_num']
        bi.user_id = info['mid']
        bi.user_name = info['author']
        bi.user_url = info['user_url']
        bi.video_type = info['type']
        bi.save(force_insert=True)
