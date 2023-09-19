# 搜狗采集系统
SOGOU_SPIDER_SYSTEM = {
    'WEIXIN_ARTICLE_SEARCH_APP_CHANNEL': {
        'TASK_SUBMIT': 'http://dts-social-public-opinion.womdata.com'
                       '/sogou-spider-system/weixin-article-search/app-channel/task/submit',
        'TASK_CANCEL': 'http://dts-social-public-opinion.womdata.com'
                       '/sogou-spider-system/weixin-article-search/app-channel/task/cancel',
        'TASK_VIEW': 'http://dts-social-public-opinion.womdata.com'
                     '/sogou-spider-system/weixin-article-search/app-channel/task/view'
    }
}

# dts告警系统
DTS_ALARM_SYSTEM = {
    'send_emil': 'http://alarm.womdata.com/dts-alarm-system/send_emil',
    'send_wechat': 'http://alarm.womdata.com/dts-alarm-system/send_wechat',
    'send_work_wechat': 'http://alarm.womdata.com/dts-alarm-system/send_work_wechat',
    'send_51wom_submit': 'http://alarm.womdata.com/dts-alarm-system/51wom/submit',
    'send_51wom_finish': 'http://alarm.womdata.com/dts-alarm-system/51wom/finish'
}

# 微信APP采集系统
WEIXIN_APP_SPIDER = {
    'submit_task': 'http://api.weixin-app-spider.womdata.com/task/create',
    'view_task': 'http://api.weixin-app-spider.womdata.com/task/detail',
    'cancel_task': 'http://api.weixin-app-spider.womdata.com/task/cancel',
}

# dts cookies池
DTS_COOKIES_POOL = {
    'get_cookies_json': 'http://cookies.womdata.com/dts_cookies_pool/get_cookies_json',
    'get_cookies_text': 'http://cookies.womdata.com/dts_cookies_pool/get_cookies_text',
}