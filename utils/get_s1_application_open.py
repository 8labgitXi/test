# -*- coding: utf-8 -*-
"""
@File        : get_s1_application_open.py
@Author      : yu wen yang
@Time        : 2022/3/17 2:34 下午
@Description :
"""
import requests
from django.http import JsonResponse

from scf_project.settings import scf_config


def s1_application_open(token):
    url = scf_config["url"]
    params = {
        "app_name": scf_config["scf_prefix"]
    }
    headers = {
        "company": scf_config["company"],
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(
        url=url,
        params=params,
        headers=headers
    )
    return response.json()


