job_manager 本地测试：
job mangager 相关3个接口：
    1.启动服务
    2.测试request
        tests/job_manager_tests.py  
        run def test_submit
        run def test_cancel
        run def test_view
    3.测试结果
        job提交正常
        dts-prod 数据库 数据表数据更新正常
        job_manager_application.log 正常  此日志用来查看任务提交的网络请求记录
        job_manager_service.log 正常      此日志用来查看任务管理执行情况
    
    
run_job 本地测试：
启动run_job 服务接口
    1.启动服务
    2.测试request:
        tests/job_manager_tests.py  
        run def test_run_job
    3.测试结果
        启动正常
        run_job_application.log 正常   此日志用来查看run_job 服务启动时间
        run_job_service.log 正常      此日志用来查看run_job 服务执行情况
        
    
    
    