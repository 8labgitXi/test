'''
@File:pwd_check.py
@DateTime:2022/4/7 17:55
@Author:xixiaoyu
@Desc:
'''
from rest_framework.exceptions import APIException


def validate_pwd(value: str):
    """
    校验密码 包含英文大小写及数字组合的密码
    :param value:
    :return:
    """
    is_digit = False
    is_lower = False
    is_upper = False
    for char in value:
        if char.isdigit():
            is_digit = True
        if char.islower() and char.isalpha():
            is_lower = True
        if char.isupper() and char.isalpha():
            is_upper = True
    if is_digit and is_lower and is_upper:
        return value
    raise APIException("密码需要同时包含大写，小写字母和数字")
