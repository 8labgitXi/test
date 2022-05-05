# -*- coding: utf-8 -*-
"""
@File        : fields.py
@Author      : niuxingjie
@Time        : 2022/3/4 17:42
@Description :
"""
from rest_framework import serializers

from consts.common import FEN_TO_YUAN
from utils.number_2_chinese import cncurrency


class FenToYuanFloatField(serializers.FloatField):
    """
    分转换成元字段：
    """
    def to_representation(self, value):
        """分-->元"""
        return "%.2f" % (value / FEN_TO_YUAN)

    def to_internal_value(self, data):
        """元-->分"""
        if isinstance(data, str) and len(data) > self.MAX_STRING_LENGTH:
            self.fail('max_string_length')
        try:
            return int(float(data) * FEN_TO_YUAN)
        except (TypeError, ValueError):
            self.fail('invalid')


class ChineseYuanFloatField(serializers.FloatField):
    """
    分转换成中文大写元字段
    """
    def to_representation(self, value):
        """分-->中文大写元"""
        yuan = value / FEN_TO_YUAN
        return cncurrency(yuan)

