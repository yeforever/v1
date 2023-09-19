#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@version: 1.0
@author: guu
@contact: yeexiao@yeah.net
@time: 19/4/2018 11:53 AM
"""


from src.config import params_common, params_local


class ParamsHelper(object):

    @classmethod
    def get_params(cls, param_name):
        """ 根据param name获得param value

        :param param_name:
        :return:
        """
        if param_name in params_local.params:
            return params_local.params[param_name]
        elif param_name in params_common.params:
            return params_common.params[param_name]
        else:
            raise Exception('%s not configured in params config!' % param_name)
