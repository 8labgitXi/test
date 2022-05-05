# -*- coding: utf-8 -*-
"""
@File        : sms.py
@Author      : liuda
@Time        : 2021/10/8 10:42
@Description : 发送短信验证码
"""
import datetime
import json
import random
import requests
from logging import getLogger

from django.core.cache import cache

from rest_framework import status
from rest_framework.exceptions import APIException

from client.models.sms import PhoneVerifyCode
from consts.sms import (
    SMS_URL,
    MAX_ERROR_TIMES,
    ONE_DAY_MAX_TIME,
    CODE_SOURCE,
    CODE_LENGTH,
    EXPIRE_TIMES,
    SMS_KEY_COMMON_TIMEOUT,
)
from scf_project.settings import sms_config
from utils.date_and_time import n_minutes_later

log = getLogger('django')


SMS_CONTENT_TEMPLATE = sms_config.get("content_template")


def send_phone_code(phone: str, code: str = None) -> bool:
    """
    发送短信验证码
    @param phone: 手机号
    @param code: 验证码
    @return: 发送结果
    """
    if code is None:
        is_ok, code = PhoneVerifyCode.create_phone_code(phone)
        if not is_ok:
            raise APIException(code)
    headers = {
        'Content-Type': 'application/json'
    }
    body = {
        "account": sms_config.get("account"),
        "password": sms_config.get("password"),
        "msg": f"【可信数据服务平台】尊敬的客户，本次操作的验证码为:{code}，5分钟内有效。如非您本人操作，请忽略该短信",
        "phone": phone
    }
    response = requests.post(
        url=SMS_URL,
        headers=headers,
        data=json.dumps(body)
    )
    if response.status_code == status.HTTP_200_OK:
        result = response.json()
        if int(result.get("code")) == 0:
            return True
        else:
            log.error(f"{phone}错误信息:{result.get('errorMsg')}")
    return False


class PhoneCodeLauncher:
    """
    短信验证码功能点:
        - 1 平台名称可配置。
        - 2 cache存储与检索各种数据。
        - 3 不同用途的验证码，文案，计算单独处理。
        - 4 较为精准的结果返回

    调试用例：
        from utils.sms import PhoneCodeLauncher
        launcher = PhoneCodeLauncher("18163959268", "login")
        launcher.send("【可信数据服务平台】尊敬的客户，本次操作的验证码为:{code}，5分钟内有效。如非您本人操作，请忽略该短信")
        launcher.validate(1245)
    """
    # key存储默认存活24小时
    KEY_COMMON_TIMEOUT = SMS_KEY_COMMON_TIMEOUT

    def __init__(self, phone, action):
        """
        几个数值说明：
            - 1 短信验证码【累计次数】:
                - 当天
                - 同一手机
            - 2 【错误次数】；
                - 当天
                - 同一手机
                - 同一种用途
                - 错误的和过期的次数
                - 连续错误次数
        @param phone: 手机号
        @param action: 用途代码，如：login，pay
        """
        day = datetime.datetime.now().today().strftime("%Y%m%d")

        # 当天累计短信验证码次数
        self.total_times_key = f"sms:{phone}:{day}:total"

        # 某种用途当天验证码错误次数key
        self.error_times_key = f"sms:{phone}:{day}:{action}:error"

        # 同一种用途的验证码的key
        self.phone_code_key = f"sms:{phone}:{action}:code"

        self.phone = phone
        self.action = action

    def validate(self, code_input):
        """
        @param code_input: 验证码
        @return:
            - 校验验证码的四种结果：
                - locked
                - expired
                - wrong
                - success
        """
        code, expire_at = cache.get_or_set(self.phone_code_key, [None, None], timeout=self.KEY_COMMON_TIMEOUT)
        error_times = cache.get_or_set(self.error_times_key, 0, timeout=self.KEY_COMMON_TIMEOUT)

        # 超出【错误次数】
        if error_times >= MAX_ERROR_TIMES:
            return "locked"

        # 通过
        if code == code_input:
            if expire_at < datetime.datetime.now():
                cache.incr(self.error_times_key)
                return "expired"
            else:
                # 验证成功后，销毁code,错误次数清0
                cache.set(self.error_times_key, 0, timeout=self.KEY_COMMON_TIMEOUT)
                cache.set(self.phone_code_key, [None, None], timeout=self.KEY_COMMON_TIMEOUT)
                return "success"
        else:
            cache.incr(self.error_times_key)
            return "wrong"

    def send(self, msg_temp):
        """
        @param msg_temp: 短信模板
        @return:
            - 发送验证码的三种结果：
                - error
                    - 发送失败
                - success
                    - 发送成功
                - overload
                    - 超出【累计次数】
                - locked
                    - 超出【错误次数】
                    - 某种用途被锁住
        """
        total_times = cache.get_or_set(self.total_times_key, 0, timeout=self.KEY_COMMON_TIMEOUT)
        error_times = cache.get_or_set(self.error_times_key, 0, timeout=self.KEY_COMMON_TIMEOUT)

        # 超出【累计次数】
        if total_times > ONE_DAY_MAX_TIME:
            return "overload"

        # 超出【错误次数】
        if error_times > MAX_ERROR_TIMES:
            return "locked"

        # 生成code调用api发送短信
        code = "".join(random.sample(CODE_SOURCE, CODE_LENGTH))
        headers = {'Content-Type': 'application/json'}
        body = {
            "account": sms_config.get("account"),
            "password": sms_config.get("password"),
            "msg": msg_temp.format(code=code),
            "phone": self.phone
        }
        response = requests.post(url=SMS_URL, headers=headers, data=json.dumps(body))
        status_code = response.status_code
        result = response.json()
        result_code = result.get("code")

        # 发送短信成功
        if status_code == status.HTTP_200_OK and result_code == "0":
            expire_at = n_minutes_later(datetime.datetime.now(), EXPIRE_TIMES)
            # 过期时间记录在value里，才能够判断出过期状态。
            cache.set(self.phone_code_key, [code, expire_at],  timeout=self.KEY_COMMON_TIMEOUT)
            cache.incr(self.total_times_key)
            return "success"
        else:
            log.error(f"{self.phone}错误信息:{result.get('errorMsg')}")
            return "error"


# 支付验证码相关
def send_pay_code(phone):
    """
    发送支付验证码
    @param phone: 手机号
    @return: 发送结果
    """
    STATUS_AND_TIPS = {
        "error": {
            "status": "error",
            "tips": "发送失败，请稍后再试！"
        },
        "success": {
            "status": "success",
            "tips": "发送成功！"
        },
        "overload": {
            "status": "overload",
            "tips": "今日发送次数超过了限制,明日再试！"
        },
        "locked": {
            "status": "locked",
            "tips": "您的短信支付验证码已经频繁错误，当日无法继续支付，次日解锁。"
        }
    }
    action = "pay"
    msg_temp = SMS_CONTENT_TEMPLATE
    launcher = PhoneCodeLauncher(phone, action)
    result = launcher.send(msg_temp)
    return STATUS_AND_TIPS[result]


def validate_pay_code(phone, code):
    """
    校验支付验证码
    @param phone: 手机号
    @param code: 验证码
    @return: 校验结果
    """
    STATUS_AND_TIPS = {
        "expired": {
            "status": "expired",
            "tips": "您的短信支付验证码已经过期，是否重新发送？",
        },
        "wrong": {
            "status": "wrong",
            "tips": "验证码错误，请输入正确的支付验证码！"
        },
        "success": {
            "status": "success",
            "tips": "验证成功！"
        },
        "locked": {
            "status": "locked",
            "tips": "您的短信支付验证码已经频繁错误，当日无法继续支付，次日解锁。"
        }
    }
    action = "pay"
    launcher = PhoneCodeLauncher(phone, action)
    result = launcher.validate(code)
    return STATUS_AND_TIPS[result]


# 登录验证码相关
def send_login_code(phone):
    """
    发送登录验证码
    @param phone: 手机号
    @return: 发送结果
    """
    STATUS_AND_TIPS = {
        "error": {
            "status": "error",
            "tips": "发送失败，请稍后再试！"
        },
        "success": {
            "status": "success",
            "tips": "发送成功！"
        },
        "overload": {
            "status": "overload",
            "tips": "今日发送次数超过了限制,明日再试！"
        },
        "locked": {
            "status": "locked",
            "tips": "您频繁多次验证码录入错误，当天已禁止您用短信验证码登录，次日解锁。"
        }
    }
    action = "login"
    msg_temp = SMS_CONTENT_TEMPLATE
    launcher = PhoneCodeLauncher(phone, action)
    result = launcher.send(msg_temp)
    return STATUS_AND_TIPS[result]


def validate_login_code(phone, code):
    """
    校验支付验证码
    @param phone: 手机号
    @param code: 验证码
    @return: 校验结果
    """
    STATUS_AND_TIPS = {
        "expired": {
            "status": "expired",
            "tips": "您的短信验证码已过有效期！",
        },
        "wrong": {
            "status": "wrong",
            "tips": "验证码错误，请输入正确的支付验证码！"
        },
        "success": {
            "status": "success",
            "tips": "验证成功！"
        },
        "locked": {
            "status": "locked",
            "tips": "您频繁多次验证码录入错误，当天已禁止您用短信验证码登录，次日解锁。"
        }
    }
    action = "login"
    launcher = PhoneCodeLauncher(phone, action)
    result = launcher.validate(code)
    return STATUS_AND_TIPS[result]


# 修改密码相关
def send_reset_code(phone):
    """
    修改密码，忘记密码--发送手机验证码
    @param phone: 手机号
    @return: 发送结果
    """
    STATUS_AND_TIPS = {
        "error": {
            "status": "error",
            "tips": "发送失败，请稍后再试！"
        },
        "success": {
            "status": "success",
            "tips": "发送成功！"
        },
        "overload": {
            "status": "overload",
            "tips": "今日发送次数超过了限制,明日再试！"
        },
        "locked": {
            "status": "locked",
            "tips": "您频繁多次验证码录入错误，当天已禁止密码修改，次日解锁。"
        }
    }
    action = "reset_forget_pwd"
    msg_temp = SMS_CONTENT_TEMPLATE
    launcher = PhoneCodeLauncher(phone, action)
    result = launcher.send(msg_temp)
    return STATUS_AND_TIPS[result]


def validate_reset_code(phone, code):
    """
    校验修改、忘记密码--手机验证码
    @param phone: 手机号
    @param code: 验证码
    @return: 校验结果
    """
    STATUS_AND_TIPS = {
        "expired": {
            "status": "expired",
            "tips": "您的短信验证码已过有效期！",
        },
        "wrong": {
            "status": "wrong",
            "tips": "验证码错误，请输入正确的验证码！"
        },
        "success": {
            "status": "success",
            "tips": "验证成功！"
        },
        "locked": {
            "status": "locked",
            "tips": "您频繁多次验证码录入错误，当天已禁止密码修改，明天再试。"
        }
    }
    action = "reset_forget_pwd"
    launcher = PhoneCodeLauncher(phone, action)
    result = launcher.validate(code)
    return STATUS_AND_TIPS[result]


if __name__ == '__main__':
    send_phone_code("13366026441", "2332")
