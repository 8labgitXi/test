# -*- coding: utf-8 -*-
"""
@File        : captcha_utils.py
@Author      : liuda
@Time        : 2021/9/26 15:24
@Description :
"""
import datetime

from rest_framework.reverse import reverse

from captcha.models import CaptchaStore


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def get_captcha(request):
    """
    获取验证码
    """
    to_json_response = dict()
    to_json_response['cptch_key'] = CaptchaStore.generate_key()
    to_json_response['cptch_image'] = reverse(
        "captcha-image",
        args=[to_json_response['cptch_key']],
        request=request,
    )
    return to_json_response


def check(user_input: str, new_cptch_key: str) -> bool:
    """验证图片验证码

    :param str user_input: 用户输入验证码
    :param str new_cptch_key: 验证码key
    :return bool: 是否成功
    """
    # 先查询验证码记录, 保证不要过期
    try:
        cptch = CaptchaStore.objects.get(
            hashkey=new_cptch_key,
            expiration__gte=datetime.datetime.now()
        )
    except CaptchaStore.DoesNotExist:
        return False

    # 全转为小写字符串判断
    if user_input.lower() == cptch.response.lower():
        # 验证完毕删除数据
        cptch.delete()
        return True

    # TODO: 可以增加失败次数差不过N次就删除这个记录，或者一次就删除，防止暴力破解
    return False
