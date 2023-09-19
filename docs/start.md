# 项目第三方库安装
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 开通http.server
cd download
nohup python3 -m http.server 51076 &

# 启动job_manager
python3 -m sanic src.applications.job_manager_application.app --host=0.0.0.0 --port=51074 --workers=2 --debug
nohup python3 -m sanic src.applications.job_manager_application.app --host=139.129.164.85 --port=51074 --workers=2 --debug > /dev/null 2>&1 &

# 启动run_job
python3 -m sanic src.applications.run_job_application.app --host=0.0.0.0 --port=51075 --workers=2 --debug
nohup python3 -m sanic src.applications.run_job_application.app --host=139.129.164.85 --port=8888 --workers=2 --debug > /dev/null 2>&1 &
curl http://139.129.164.85:51075/dts-auto-brief/run_job
