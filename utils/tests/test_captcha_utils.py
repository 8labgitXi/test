# -*- coding: UTF-8 -*-
"""
@Summary : 测试验证码相关工具
@Author  : Rey
@Time    : 2022-03-18 13:40:25
@Run     : python manage.py test utils.tests.test_captcha_utils  -v=3 --keepdb
"""
from datetime import datetime, timedelta

from rest_framework.test import APITestCase

from captcha.models import CaptchaStore
from utils import captcha_utils


class TestCheck(APITestCase):
    """测试检查验证码"""

    def test_success_1(self):
        """测试成功: 验证码是大小写混合, 输入是纯小写"""

        cs = 'gpvJ'
        hash_key = 'd64289c54675747b69036c389f829aab20ae51ea'
        CaptchaStore.objects.create(
            id=1, 
            challenge='GPVJ',
            response=cs,
            hashkey=hash_key,
            expiration=datetime.now() + timedelta(minutes=5)
        )

        self.assertTrue(captcha_utils.check(cs.lower(), hash_key))

        with self.assertRaises(CaptchaStore.DoesNotExist):
            CaptchaStore.objects.get(id=1)
    
    def test_success_2(self):
        """测试成功: 验证码是大小写混合, 输入是纯大写"""

        cs = 'gpvJ'
        hash_key = 'd64289c54675747b69036c389f829aab20ae51ea'
        CaptchaStore.objects.create(
            id=1, 
            challenge='GPVJ',
            response=cs,
            hashkey=hash_key,
            expiration=datetime.now() + timedelta(minutes=5)
        )

        self.assertTrue(captcha_utils.check(cs.upper(), hash_key))

    def test_success_3(self):
        """测试成功: 验证码是大小写混合, 输入是大小写混合"""

        cs = 'gpvJ'
        hash_key = 'd64289c54675747b69036c389f829aab20ae51ea'
        CaptchaStore.objects.create(
            id=1, 
            challenge='GPVJ',
            response=cs,
            hashkey=hash_key,
            expiration=datetime.now() + timedelta(minutes=5)
        )

        self.assertTrue(captcha_utils.check('GPvJ', hash_key))
    
    def test_fail_1(self):
        """测试失败: hashkey不存在"""

        cs = 'gpvJ'
        hash_key = 'd64289c54675747b69036c389f829aab20ae51ea'
        CaptchaStore.objects.create(
            id=1, 
            challenge='GPVJ',
            response=cs,
            hashkey=hash_key,
            expiration=datetime.now() + timedelta(minutes=5)
        )

        self.assertFalse(captcha_utils.check('GPvJ', hash_key[:-1]))
    
    def test_fail_2(self):
        """测试失败: 过期"""

        cs = 'gpvJ'
        hash_key = 'd64289c54675747b69036c389f829aab20ae51ea'
        CaptchaStore.objects.create(
            id=1, 
            challenge='GPVJ',
            response=cs,
            hashkey=hash_key,
            expiration=datetime.now() - timedelta(minutes=5)
        )

        self.assertFalse(captcha_utils.check('GPvJ', hash_key))
    
    def test_fail_3(self):
        """测试失败: 字符串验证码,输入是字符串"""

        cs = 'gpvJ'
        hash_key = 'd64289c54675747b69036c389f829aab20ae51ea'
        CaptchaStore.objects.create(
            id=1, 
            challenge='GPVJ',
            response=cs,
            hashkey=hash_key,
            expiration=datetime.now() - timedelta(minutes=5)
        )

        self.assertFalse(captcha_utils.check('aa', hash_key))
    
    def test_fail_4(self):
        """测试失败: 数字验证码,输入是字符串"""

        cs = '1234'
        hash_key = 'd64289c54675747b69036c389f829aab20ae51ea'
        CaptchaStore.objects.create(
            id=1, 
            challenge='GPVJ',
            response=cs,
            hashkey=hash_key,
            expiration=datetime.now() - timedelta(minutes=5)
        )

        self.assertFalse(captcha_utils.check('aa', hash_key))
    
    def test_fail_5(self):
        """测试失败: 字符串验证码,输入是数字"""

        cs = 'gpvJ'
        hash_key = 'd64289c54675747b69036c389f829aab20ae51ea'
        CaptchaStore.objects.create(
            id=1, 
            challenge='GPVJ',
            response=cs,
            hashkey=hash_key,
            expiration=datetime.now() - timedelta(minutes=5)
        )

        self.assertFalse(captcha_utils.check('1234', hash_key))
