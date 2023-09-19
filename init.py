#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目初始化
> python3 init.py

命令行参数里指定 dev or prod, 在项目的config目录下生成相应配置文件

@version: 1.0
@author: guu
@contact: yeexiao@yeah.net
@time: 7/8/17 9:24 PM
"""

import sys
import os

from configparser import ConfigParser

from boost_py.helpers.core.file_helper import FileHelper
from boost_py.helpers.core.server_helper import ServerHelper

current_work_directory = os.getcwd()  # 当前目录
project_directory = os.path.dirname(os.path.realpath(__file__))  # 项目目录
project_name = project_directory.split('/')[-1]


def init_main_conf():
    """ 初始化配置文件main.py
    TODO environment main_local 不存在时，在src/config下新建 main_local.py

    :return:
    """
    # main.py源路径
    src_main_conf = '{current_work_directory}/environments/{env}/config/main.py'.format(
            current_work_directory=current_work_directory,
            env=env)

    # main.py 和 main_local.py目标路径
    dest_main_conf = '{current_work_directory}/src/config/main.py'.format(
            current_work_directory=current_work_directory)
    dest_main_local_conf = '{current_work_directory}/src/config/main_local.py'.format(
            current_work_directory=current_work_directory)

    if not FileHelper.exist(src_main_conf):
        exit('\n[ERROR] init main conf.')
    else:
        FileHelper.copy(src_main_conf, dest_main_conf)
        FileHelper.copy(src_main_conf, dest_main_local_conf)

    # 初始化文件里的变量
    FileHelper.replace_content(dest_main_conf, '{path}', os.getcwd() if 'C:\\' not in os.getcwd() else os.getcwd().replace('C:\\', 'C:\\\\'))

    print('\n[OK] init main conf.')
    return True


def init_params_conf():
    """ 初始化参数配置文件

    :return:
    """
    src_common_params_conf = '{current_work_directory}/environments/common/config/params.py'.format(
            current_work_directory=current_work_directory)
    src_local_params_conf = '{current_work_directory}/environments/{env}/config/params.py'.format(
            current_work_directory=current_work_directory,
            env=env)
    dest_common_params_conf = '{current_work_directory}/src/config/params_common.py'.format(
            current_work_directory=current_work_directory)
    dest_local_params_conf = '{current_work_directory}/src/config/params_local.py'.format(
            current_work_directory=current_work_directory)

    FileHelper.copy(src_common_params_conf, dest_common_params_conf)
    FileHelper.copy(src_local_params_conf, dest_local_params_conf)

    print('[OK] init params conf.')
    return True


def init_service_conf():
    src_service_conf = '{current_work_directory}/environments/{env}/config/services.py'.format(
            current_work_directory=current_work_directory,
            env=env)
    dest_service_conf = '{current_work_directory}/src/config/services.py'.format(
            current_work_directory=current_work_directory)

    FileHelper.copy(src_service_conf, dest_service_conf)

    print('[OK] init service conf.')
    return True


def _generate_supervisor_config():
        """ 生成supervisor配置文件

        :return:
        """
        address_list = ServerHelper.get_address_list()

        supervisor_config_root_dir = ''

        from src.config.supervisor import supervisor_config, program_config
        to_deploy_program_groups = {}
        for program_name in program_config:
            _program_deploy_config = program_config[program_name]
            for _config in _program_deploy_config:
                if _config['ip'] in address_list:
                    # 该program应该部署在该服务器上
                    supervisor_config_root_dir = supervisor_config[_config['ip']]['supervisor_conf_dir']
                    to_deploy_program_groups[program_name] = {
                        'project_root_dir': project_directory,
                        'supervisor_conf_dir': supervisor_config[_config['ip']]['supervisor_conf_dir'],
                        'supervisor_log_dir': supervisor_config[_config['ip']]['supervisor_log_dir'],
                        'cmd': _config['cmd']
                    }

        if len(to_deploy_program_groups) == 0:
            return False

        conf_parser = ConfigParser()
        conf_parser['group:%s' % project_name] = {
            'programs': ','.join(to_deploy_program_groups)
        }
        for program_name in to_deploy_program_groups:
            conf_parser['program:%s' % program_name] = {
                'command': to_deploy_program_groups[program_name]['cmd'],
                'directory': to_deploy_program_groups[program_name]['project_root_dir'],
                'autostart': 'true',
                'autorestart': 'true',
                'stdout_logfile': '{supervisor_log_dir}/{log_file}'.format(supervisor_log_dir=to_deploy_program_groups[program_name]['supervisor_log_dir'],
                                                                           log_file=program_name+'.log'),
                'stderr_logfile': '{supervisor_log_dir}/{error_log_file}'.format(supervisor_log_dir=to_deploy_program_groups[program_name]['supervisor_log_dir'],
                                                                                 error_log_file=program_name+'.error.log'),
                'stopasgroup': 'true'
            }
        supervisor_deploy_config_file = '{project_directory}/deployment/{file_name}'.format(project_directory=project_directory,
                                                                                            file_name=project_name+'.supervisor.conf')
        with open(supervisor_deploy_config_file, 'w') as _file:
            conf_parser.write(_file)

        return {
            'supervisor_deploy_config': supervisor_deploy_config_file,
            'supervisor_config_root_dir': supervisor_config_root_dir + '/' + project_name+'.supervisor.conf'
        }


def init_supervisor_deploy_conf():
    """ 服务部署配置文件

    :return:
    """
    src_supervisor_conf = '{current_work_directory}/environments/{env}/config/supervisor.py'.format(
            current_work_directory=current_work_directory,
            env=env)
    dest_supervisor_conf = '{current_work_directory}/src/config/supervisor.py'.format(
            current_work_directory=current_work_directory)

    FileHelper.copy(src_supervisor_conf, dest_supervisor_conf)

    # 生成supervisor配置文件
    rtn = _generate_supervisor_config()
    if not rtn:
        print('[FAIL] init supervisor deploy config.')
        print('ERROR MESSAGE: current server not configured in the supervisor config')
        return False

    print('[OK] init supervisor deploy config.')

    # 将supervisor配置文件移动本地服务器supervisor目录下
    supervisor_deploy_config = rtn['supervisor_deploy_config']
    supervisor_config_root_dir = rtn['supervisor_config_root_dir']

    FileHelper.copy(src=supervisor_deploy_config, dst=supervisor_config_root_dir)
    return True


def init_runtime():
    """ 初始化runtime

    :return:
    """
    runtime_directory = '{project_directory}/runtime'.format(project_directory=project_directory)
    log_directory = '{project_directory}/runtime/logs'.format(project_directory=project_directory)

    FileHelper.makedir(runtime_directory, False)
    FileHelper.makedir(log_directory, False)

    print('[OK] init runtime.')
    return True


if __name__ == '__main__':
    print('\n  Which environment do you want the project to be initialized in?\n')
    print('  [0] Development \n  [1] Production')
    while True:
        choice = input('Your choice [0-1, or \"q\" to quit] ')
        if choice != '' and choice.lower() in ['0', '1', 'q']:
            choice = choice.lower()
            break
    if choice == 'q':
        sys.exit(0)
    elif choice == '0':
        env = 'dev'
    elif choice == '1':
        env = 'prod'

    while True:
        double_check = input("Initialize the application under '%s' environment? [yes|no] " % env)
        if double_check != '' and double_check.lower() in ['yes', 'no']:
            break

    init_main_conf()
    init_params_conf()
    init_service_conf()
    init_runtime()

    print('\n')
