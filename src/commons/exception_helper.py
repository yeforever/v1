"""
@version: 1.0
@author: anne
@contact: thy.self@foxmail.com
@time: 2021/11/22 下午3:26
"""
from merry import Merry

merry = Merry()
merry.logger.disabled = True
merry_except = merry._except(Exception)
merry_try = merry._try


# 定义except 未知异常返回None
@merry_except
def process_exception(e):
    # logger
    return None
