# -*- coding: utf-8 -*-
"""
@File        : fen_and_yuan.py
@Author      : yu wen yang
@Time        : 2022/3/14 3:00 下午
@Description :
"""
from consts.common import FEN_TO_YUAN
from decimal import Decimal

def fen_to_yuan(fen):
    """
    分转换成元
    @param fen:   分
    @return:   浮点数类型的元
    """
    return "%.2f" % (fen / FEN_TO_YUAN) if fen else "0.00"


def yuan_to_fen(yuan):
    """
    元转换为分:
        - 如果元是浮点数，分后的将被舍弃
        - 如果
    @param yuan:   元
    @return:   分
    """
    return int(Decimal(yuan).quantize(Decimal("0.00")) * FEN_TO_YUAN)


def yuan2fen(val):
    """ 字符串的元转整型的分

    @param val: 字符串的元
    @return:
    """
    return int(Decimal(val).quantize(Decimal("0.00")) * FEN_TO_YUAN)
