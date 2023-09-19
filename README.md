dts-auto-brief-v1
=================================

### 安装部署(docker)

```bash
git clone git@139.129.229.82:qmg/dts-auto-brief-v1.git
cd dts-auto-brief-v1
python3 init.py
cd docker
sh build.sh
sh start_contain.sh
```

### jenkins（集成部署）

```
url:http://dev.jenkins.51wom.com/
login: taohongyang / QM888888
视图： 数据组
项目： sjz-dts-auto-brief
exec command: 
	echo "start" && cd /alidata1/workpace/dts-auto-brief-v1/ && git pull && cd docker && sh rebuild_project.sh
```

### 本地调试

```
worker 启动命令
  celery -A src.services.worker.mweibo_worker.app worker -l info -P gevent -c 60
  celery -A src.services.worker.weixin_worker.app worker -l info -P gevent -c 60
  celery -A src.services.worker.redbook_worker.app worker -l info -P gevent -c 60
  celery -A src.services.worker.douyin_worker.app worker -l info -P gevent -c 60
  celery -A src.services.worker.bili_worker.app worker -l info -P gevent -c 60

kafka consumer 启动命令
  python3 -m src.services.kafka.kafka_weibo_consumer
  python3 -m src.services.kafka.kafka_weixin_consumer
  python3 -m src.services.kafka.kafka_redbook_consumer
  python3 -m src.services.kafka.kafka_douyin_consumer
  python3 -m src.services.kafka.kafka_bili_consumer
  
job manager 启动命令
	python3 -m src.applications.job_manager
```

### docker 私服(暂无)

### nginx 配置

```
文件名： brief.conf
upstream brief {
        server  106.15.138.230:8999;
}

http: 
server {
        listen  80;
        server_name  brief.womdata.com;
        access_log /alidata1/wwwlogs/dts-core.womdata.com/access_nginx.log combined;

	proxy_pass_header Server;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        
https:
server {
        listen       443 ssl http2 default_server;
        listen       [::]:443 ssl http2 default_server;
        server_name  brief.womdata.com;
        
        ssl_certificate "/alidata1/pem/5840437_brief.womdata.com.pem";
        ssl_certificate_key "/alidata1/pem/5840437_brief.womdata.com.key";
        ssl_session_cache shared:SSL:1m;
        ssl_session_timeout  10m;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

```

### api逻辑

```
文件： job_manager.py
/dts-auto-brief/job/submit  在用
/dts-auto-brief/job/view  在用
/dts-auto-brief/job/search  在用
/dts-auto-brief/job/view_article_list  在用
/dts-auto-brief/job/view_account_list  在用

/dts-auto-brief/job/cancel  弃用
/dts-auto-brief/job/change  弃用
/dts-auto-brief/job/spider_progress  弃用
```

### model

```
job_model.py  取别名，简化代码
改表名和改表字段 务必注意修改model
```

### data 目录下的结构
```
- stage_uuid.zip
- stage_uuid/
    - keyword.xlsx
    - keyword_analysis.xlsx
    - content_wc.png
    - topic_wc.png
```


### 采集逻辑

```
接口异步任务 -> celery -> gevent 60 处理 -> 数据异步发送kafka -> kafka 消费者进程 执行 存储mysql
server 负责 发送任务 和 excel 分析导出
worker 负责 数据采集
kafka 负责 数据存储
```

### 新版优化思路

```
1.接口层只负责处理 mysql 查询和 异步任务发送， 降低延时
2.采集层拆分 采集 存储 分析 3个部分，异步通信 并行执行任务， 降低执行时间
3.引入 celery kafka 2种消息队列 
		celery(redis) 内存有限，仅应用于任务消息传递
		kafka 传递工单数据，数据量较大，使用redis 容易把内存资源吃完，所以选择kafka ,后续方便接入flink
```

### mysql 表 各平台 通用字段表
```
url  				作品url
title/content 		作品title/tontent
post_time			作品发布时间
like 				作品点赞
read				作品阅读
share				作品转发/分享
comment				作品评论
collect				作品收藏
play				作品播放
danmu				作品弹幕
download			作品下载	
interraction		作品互动
user_name			用户名
user_fans 			用户粉丝数
user_fans_level		用户粉丝数级别
```

### peewee 自动导出model命令
```
python3 -m pwiz -e mysql -H rm-m5ex13f9qkq9s0w0aso.mysql.rds.aliyuncs.com -p 3306 -P -u dts_prod_admin dts_dev > model.py

i7ny34d87snu7162$
```

### 几个体验上的问题如何优化
```
1. whosecard 接口 小红书 延时过高，链路过长，重试和接口错误问题如果优化
2. celery 任务异步采集， 如何获取task 结束时间
3. 导出数据jieba 切词时间 1-2s, 关键词多的情况下，导出时间过长，如何解决
4. 提交工单 - 数据完全采集结束  时间不可控如何保证是 秒级 执行完这些操作
```


