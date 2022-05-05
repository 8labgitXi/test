# -*- coding: utf-8 -*-
"""
@File        : filters.py
@Author      : niuxingjie
@Time        : 2022/4/15 14:59
@Description :
"""
from datetime import datetime, time

from django import forms

from django_filters import RangeFilter
from django_filters.fields import RangeField
from django_filters.widgets import DateRangeWidget
from django_filters.utils import handle_timezone

from utils.date_and_time import get_period


class MonthDateField(forms.DateField):
    """
    重写月份校验字段：
        - 2006-10
    """
    input_formats = ["%Y-%m"]


class MonthDateRangeField(RangeField):
    """
    自定义月份起止过滤字段:
        - start: 2022-01  --> 2022-01-01
        - end: 2022-02 --> 2022-02-28
    """
    widget = DateRangeWidget

    def __init__(self, *args, **kwargs):
        fields = (
            MonthDateField(),
            MonthDateField(),
        )
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            start_date_month, stop_date_month = data_list

            # 增加对月份第一天和最后一天的处理
            start_date, _ = get_period(str(start_date_month))
            _, stop_date = get_period(str(stop_date_month))

            if start_date:
                start_date = handle_timezone(
                    datetime.combine(start_date, time.min),
                    False
                )
            if stop_date:
                stop_date = handle_timezone(
                    datetime.combine(stop_date, time.max),
                    False
                )
            return slice(start_date, stop_date)
        return None


class MonthFromToRangeFilter(RangeFilter):
    """
    用于月份范围内数据字段的过滤：
        - 2022-01到2024-02之间的数据
            - 2022-01-01 00:00:00
            - 2024-02-29 23:59:59.999999
    使用示例：
        - 过滤字段用法：
            sign = MonthFromToRangeFilter(field_name='credit_certificate__confirm_at')
        - 输入两个字段：
            - sign_after --> 2022-01
            - sign_before --> 2024-02
    """
    field_class = MonthDateRangeField
