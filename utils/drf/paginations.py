# -*- coding: utf-8 -*-
"""
@File        : paginations.py
@Author      : yu wen yang
@Time        : 2022/1/24 9:12 上午
@Description :
"""
from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class MyPageNumberPagination(PageNumberPagination):
    """
    指定页码和显示数量分页
    """
    # 默认每页显示数量
    page_size = 20
    # url中每页显示条数的参数
    page_size_query_param = 'size'
    # url中页码的参数
    page_query_param = 'page'
    # 每页最多显示多少条
    max_page_size = 50

    def get_paginated_response(self, data):
        """
        重写返回结果
        :param data:
        :return:
        """
        return Response(OrderedDict([
            ('total', self.page.paginator.count),
            ('current_page', self.page.number),
            ('page_range', list(self.page.paginator.page_range)),
            ('list', data)
        ]))
