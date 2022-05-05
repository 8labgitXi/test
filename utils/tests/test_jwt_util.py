# -*- coding: UTF-8 -*-
"""
@Summary : 测试jwt_util
@Author  : Rey
@Time    : 2022-03-23 14:41:56
@Run     : python manage.py test utils.tests.test_jwt_util  -v=3 --keepdb
"""
from datetime import datetime, timedelta

from django.test import SimpleTestCase
import jwt

from utils.jwt_util import user_info_2_token, token_2_user_info, SECRET_KEY


class TestUserInfo2Token(SimpleTestCase):
    """测试jwt_util.user_info_2_token"""

    def test_success_no_expire_time(self):
        """测试成功: 未指定过期时间"""
        ori_user_info = {'user_id': 1}
        encoded_jwt = user_info_2_token(ori_user_info)
        decode_user_info = jwt.decode(encoded_jwt, verify=False)
        self.assertEqual(ori_user_info['user_id'], decode_user_info['user_id'])
        self.assertIn('expire_time', decode_user_info)

    def test_success_specify_expire_time(self):
        """测试成功: 指定过期时间"""
        expire_time = str(datetime.now())
        ori_user_info = {'user_id': 1, 'expire_time': expire_time}
        encoded_jwt = user_info_2_token(ori_user_info)
        decode_user_info = jwt.decode(encoded_jwt, verify=False)
        self.assertEqual(ori_user_info['user_id'], decode_user_info['user_id'])
        self.assertIn('expire_time', decode_user_info)
        self.assertEqual(decode_user_info['expire_time'], expire_time)


class TestToken2UserInfo(SimpleTestCase):
    """测试jwt_util.token_2_user_info"""

    def test_success(self):
        """测试成功解析"""
        ori_user_info = {'user_id': 1, 'expire_time': str(datetime.now()+timedelta(minutes=5))}
        encoded_jwt = jwt.encode(ori_user_info, SECRET_KEY, algorithm='HS256')
        decode_user_info = token_2_user_info(encoded_jwt)
        self.assertDictEqual({'user_id': 1}, decode_user_info)
        self.assertNotIn('expire_time', decode_user_info)

    def test_no_user_info(self):
        """测试user_info为空"""
        ori_user_info = {}
        encoded_jwt = jwt.encode(ori_user_info, SECRET_KEY, algorithm='HS256')
        decode_user_info = token_2_user_info(encoded_jwt)
        self.assertIsNone(decode_user_info)

    def test_no_expire_time(self):
        """测试jwt中无expire_time信息"""
        ori_user_info = {'user_id': 1}
        encoded_jwt = jwt.encode(ori_user_info, SECRET_KEY, algorithm='HS256')
        decode_user_info = token_2_user_info(encoded_jwt)
        self.assertIsNone(decode_user_info)

    def test_expire(self):
        """测试jwt过期"""
        ori_user_info = {
            'user_id': 1,
            'expire_time': str(datetime.now() - timedelta(minutes=1))
        }
        encoded_jwt = jwt.encode(ori_user_info, SECRET_KEY, algorithm='HS256')
        decode_user_info = token_2_user_info(encoded_jwt)
        self.assertIsNone(decode_user_info)
