类方法说明：

submit_task(cls):
    提交brief任务
    1.任务提交json格式
    {task_data: {
        'redbook': ['美妆', '分享', '完美日记', '小金瓶', 'olay', '欧莱雅'],
        'weixin': ['完美日记', '小金瓶'],
        'mweibo': ['美妆', '分享'],
        'bilibili': ['美妆', '分享']
        }
    }
    2.条件判断
    a.判断json格式是否正确
    b.判断json 内 k值 是否正确
    c.判断keywords value值 是否是列表格式
    3.任务提交
    将任务数据，存储到数据库中
    

cancel_task(cls):
    取消brief任务
    更改task表状态，改为取消状态，然后中断采集操作 -> return True


view_task(cls):
    查看brief任务
    根据task_uuid 或者 其他条件，查询task表状态，将查表数据存到json, -> return json


view_job(cls):
    查看brief全部任务
    直接查询所有brief信息，存到json  -> return json
    

view_brief_rar_path(cls):
    查看brief打包文件路径
    一个brief_task 采集完的所有数据，导出成excel, 并打包成rar, 上传到服务器目录下， 该目录开启http_server , 打包文件对应一个url.返回此url


view_brief_status(cls):
    查看brief执行状态
    brief 开始和结束 时间均有记录，通过查表，查询brief 的结束时间，来判断当前brief 是否完成，将状态记录到status - > return status
