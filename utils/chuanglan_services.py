# -*- coding: utf-8 -*-
"""
@File        : chuanglan_services.py
@Author      : yu wen yang
@Time        : 2022/4/1 10:50 上午
@Description :
"""
import logging
import re

import requests
from typing import Union
from rest_framework import status

from consts.common import SUCCESS_CODE
from scf_project.settings import chuanglan_config

logger = logging.getLogger('supply_chain_app')


class OcrRecognition(object):
    """
    ocr识别
    """

    def __init__(self):
        self.app_id = chuanglan_config["app_id"]
        self.app_key = chuanglan_config["app_key"]

    def is_success_request(self, res):
        if res.status_code == status.HTTP_200_OK and res.json()["code"] == SUCCESS_CODE:
            return True
        return False

    def business_license(self, base64_image) -> Union[dict, None]:
        """
        营业执照
        @param base64_image:
        @return:
        """
        res = requests.post(
            url=chuanglan_config["business_license_url"],
            data={
                "appId": self.app_id,
                "appKey": self.app_key,
                "image": base64_image,
                "fixMode": "1",  # "1"修复模式; "0"不修复模式
            }
        )
        const = {
            '社会信用代码': 'credit',
            '经营范围': 'management_range',
            '成立日期': 'establish_at',
            '法人': 'legal_per_name',
            '注册资本': 'registered_capital',
            '地址': 'registered_address',
            '单位名称': 'name',
        }
        if self.is_success_request(res):
            resp = res.json()["data"]["data"]["words_result"]
            resp = {const[k]: v["words"] for k, v in resp.items() if const.get(k)}
            resp["establish_at"] = resp["establish_at"].replace("年", "-")
            resp["establish_at"] = resp["establish_at"].replace("月", "-")
            resp["establish_at"] = resp["establish_at"].replace("日", "")
            registered_capital = resp["registered_capital"]
            regex = r"\d+\.?\d*"
            try:
                ret = re.search(regex, registered_capital).group()
            except AttributeError as err:
                logger.error(f"request chuanglan [business_license] error: {str(err)}")
                return
            resp["registered_capital"] = ret
            return resp
        logger.error(f"request chuanglan [business_license] error: {res.json()}")
        return None

    def id_card(self, base64_image, ocr_type) -> Union[dict, None]:
        """
        身份证
        @param base64_image:
        @param ocr_type:
        @return:
        """
        res = requests.post(
            url=chuanglan_config["id_card_url"],
            data={
                "appId": self.app_id,
                "appKey": self.app_key,
                "image": base64_image,
                "imageType": "BASE64",
                "ocrType": ocr_type,  # "0"正面; "1"反面
            }
        )
        if self.is_success_request(res):
            return res.json()["data"]
        logger.error(f"request chuanglan [id_card] error: {res.json()}")
        return None

    def business_four_auth(
            self, company_name: str, legal_per_name: str, credit_code: str, id_num: str
    ) -> Union[dict, None]:
        """
        企业工商四要素
        @param company_name: 企业姓名
        @param legal_per_name: 法人姓名
        @param credit_code: 统一信用代码
        @param id_num: 法人身份证
        @return:
        """
        res = requests.post(
            url=chuanglan_config["business_four_auth"],
            data={
                "appId": self.app_id,
                "appKey": self.app_key,
                "entName": company_name,
                "legalPerName": legal_per_name,
                "creditCode": credit_code,
                "idNum": id_num
            }
        )
        if self.is_success_request(res):
            data = res.json()["data"]
            company_name_match = data.get("companyNameMatch") == "1"
            credit_code_match = data.get("creditCodeMatch") == "1"
            legal_per_name_match = data.get("legalPerNameMatch") == "1"
            id_no_match = data.get("idNoMatch") == "1"
            return company_name_match and credit_code_match and legal_per_name_match and id_no_match

        logger.error(f"request chuanglan [business_four_auth] error: {res.json()}")
        return None
