# -*- coding: utf-8 -*-
"""
@File        : phone_and_email_re.py
@Author      : liuda
@Time        : 2021/9/29 10:22
@Description : 校验工具
"""
import re
from rest_framework.serializers import ValidationError


def phone_validator(phone: str) -> str:
    """
    手机号验证
    @param phone:
    @return:
    """
    ret = re.match(r"^1[3456789]\d{9}$", phone)
    if ret:
        return phone
    raise ValidationError("手机号不合法")


def identifier_validator(string):
    """
    检验用于变量的标识符
    @param string:
    @return:
    """
    regex = r'^[A-Za-z_][A-Za-z0-9_]*$'
    ret = re.match(regex, string)
    if ret:
        return string
    raise ValidationError("标识符不合法")
