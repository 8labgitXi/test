# -*- coding: utf-8 -*-
"""
@File        : decrypted.py
@Author      : yu wen yang
@Time        : 2022/3/28 11:59 上午
@Description :
"""
import binascii

from pyDes import des, CBC, PAD_PKCS5


def des_decrypt(s: str, secret_key: str = "$c1&md&d"):
    """
    解密
    :param s: 加密后的字符串，16进制
    :param secret_key: 加密后的字符串，16进制
    :return:  解密后的字符串
    """
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
    return de.decode('utf8')
