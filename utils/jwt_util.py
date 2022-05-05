# @Time : 2021/8/19

# @Author : liuda

# @File : jwt_util.py

# @Description : jwt 工具函数

from typing import Union

import jwt

from datetime import datetime, timedelta
# 使用Django中的 SECRET_KEY 就打开下面的注释
# from django.conf import settings

# SECRET_KEY = settings.SECRET_KEY
SECRET_KEY = "s1ni#lua2d-1)_&@0na=#m5bb1p&nvh%levjr2oo5x-lq##o9i"


def user_info_2_token(user_info: dict, expire_days: int = 30) -> str:
    """
    获取jwt token
    :param user_info: 用户信息
    :param expire_days: 过期天数，默认一天
    :return: jwt token
    """
    # 不修改输入, 重新赋值
    token_info = {key: user_info[key] for key in user_info}
    # 设置过期时间
    if "expire_time" not in token_info:
        token_info["expire_time"] = str(datetime.now() + timedelta(days=expire_days))
    encoded_jwt = jwt.encode(token_info, SECRET_KEY, algorithm='HS256')
    return encoded_jwt


def token_2_user_info(token: str) -> Union[dict, None]:
    """
    jwt token 转成user信息
    :param token: jwt token
    :return: 用户信息或None
    """
    user_info = jwt.decode(token, verify=False)
    if not user_info or "expire_time" not in user_info:
        return None
    expire_time = datetime.strptime(user_info["expire_time"].split(".")[0], '%Y-%m-%d %H:%M:%S')
    # 判断是否过期
    if (expire_time - datetime.now()).total_seconds() < 0:
        return None
    user_info.pop("expire_time")
    return user_info
