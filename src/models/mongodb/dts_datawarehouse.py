#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@version: 1.0
@author: guu
@contact: yeexiao@yeah.net
@time: 17/4/2018 11:48 AM
"""
from boost_py.databases.mongodb import BaseMongoCollection
from src.config.main import mongodb_config

DB_NAME = 'wom-dts-datawarehouse'


class BriefTaskRedbookArticleListCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_task_redbook_article_list_collections'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefTaskRedbookArticleListCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefTaskRedbookArticleListCollections.COLLECTION_NAME


class BriefTaskRedbookArticleDetailCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_task_redbook_article_detail_collections'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefTaskRedbookArticleDetailCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefTaskRedbookArticleDetailCollections.COLLECTION_NAME


class BriefTaskMweiboArticleCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_task_mweibo_article_collections'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefTaskMweiboArticleCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefTaskMweiboArticleCollections.COLLECTION_NAME


class BriefTaskWeiboCnArticleCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_task_weibo_cn_article_collections'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefTaskWeiboCnArticleCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefTaskWeiboCnArticleCollections.COLLECTION_NAME


class BriefTaskWeiboComArticleCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_task_weibo_com_article_collections'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefTaskWeiboComArticleCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefTaskWeiboComArticleCollections.COLLECTION_NAME


class BriefStageMweiboAccountListCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_stage_mweibo_account_list_collication'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefStageMweiboAccountListCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefStageMweiboAccountListCollections.COLLECTION_NAME


# brief_stage_redbook_account_list_collication
class BriefStageRedbookAccountListCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_stage_redbook_account_list_collication'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefStageRedbookAccountListCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefStageRedbookAccountListCollections.COLLECTION_NAME


class BriefStageRedbookArticleDetailCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_task_redbook_article_detail_collections'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefStageRedbookArticleDetailCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefStageRedbookArticleDetailCollections.COLLECTION_NAME


class BriefTaskRedbookArticleCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_task_redbook_article_collections'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefTaskRedbookArticleCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefTaskRedbookArticleCollections.COLLECTION_NAME


# brief_task_redbook_article_collections
class BriefTaskRedbookAccountListCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_stage_redbook_account_list_collication'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefTaskRedbookAccountListCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefTaskRedbookAccountListCollections.COLLECTION_NAME


class BriefTaskWeixinArticleCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_task_weixin_article_collections'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefTaskWeixinArticleCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefTaskWeixinArticleCollections.COLLECTION_NAME


class BriefStageWeiXinAccountListCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_stage_weixin_account_list_collection'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefStageWeiXinAccountListCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefStageWeiXinAccountListCollections.COLLECTION_NAME


class BriefTaskBiliArticleCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_task_bili_article_collections'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefTaskBiliArticleCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefTaskBiliArticleCollections.COLLECTION_NAME


class BriefStageBiliAccountListCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_stage_bili_account_list_collection'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefStageBiliAccountListCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefStageBiliAccountListCollections.COLLECTION_NAME


class BriefTaskDouyinArticleCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_task_douyin_article_collections'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefTaskDouyinArticleCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefTaskDouyinArticleCollections.COLLECTION_NAME


class BriefStageDouYinAccountListCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_stage_douyin_account_list_collection'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefStageDouYinAccountListCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefStageDouYinAccountListCollections.COLLECTION_NAME


class BriefTaskKwaiArticleCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_task_kwai_article_collections'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefTaskKwaiArticleCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefTaskKwaiArticleCollections.COLLECTION_NAME


class BriefTaskZhihuArticleCollections(BaseMongoCollection):
    COLLECTION_NAME = 'brief_task_kwai_article_collections'

    def __init__(self):
        super().__init__(db_name=DB_NAME,
                         db_config=mongodb_config[DB_NAME],
                         collection_name=BriefTaskZhihuArticleCollections.COLLECTION_NAME)

    @classmethod
    def table_name(cls):
        return BriefTaskZhihuArticleCollections.COLLECTION_NAME
