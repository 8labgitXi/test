# -*- coding: utf-8 -*-
"""
@File        : db_util.py
@Author      : wst
@Time        : 2022/4/7 下午6:22
@Description : 数据库相关的函数
"""

from django.db.models import Aggregate, IntegerField
from django.contrib.postgres.fields import ArrayField


class GroupConcat(Aggregate):
    function = "array_agg"
    template = "%(function)s(%(expressions)s)"

    def __init__(self, expression, **extra):
        super(GroupConcat, self).__init__(
            expression,
            output_field=ArrayField(base_field=IntegerField()),
            **extra
        )
