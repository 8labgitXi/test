# -*- coding: UTF-8 -*-
"""
@Summary : docstr
@Author  : Rey
@Time    : 2022-04-19 13:20:27
@Run     : python manage.py test utils.tests.test_chain  -v=3 --keepdb
"""
from django.test import SimpleTestCase

from utils.data_2_chain import ChainUtil


class TestChain(SimpleTestCase):
    def test_1(self):
        obj = ChainUtil()
        print(obj.transfer({'name': 1}))
