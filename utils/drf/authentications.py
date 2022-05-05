# -*- coding: utf-8 -*-
"""
@File        : authentications.py
@Author      : liuda
@Time        : 2021/10/4 17:30
@Description : 登陆认证器
"""
import datetime
import re

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, APIException

from client.models.company import S1UserCompanyMap, CompanyReviewLog, Company
from client.models.role import UserRole
from consts.common import NORMAL_CACHE_TIME
from scf_project.settings import scf_config
from utils.get_s1_application_open import s1_application_open
from utils.jwt_util import token_2_user_info
UserModel = get_user_model()


MANAGEMENT_PATH_PREFIX = '^/api/v(1|1_1_0)/scf/management/'
CLIENT_V1_1_0_PREFIX = '^/api/v1_1_0/scf/client'

ALL_COMPANY_PATH = [
    f"{CLIENT_V1_1_0_PREFIX}/notice/",
    f"{CLIENT_V1_1_0_PREFIX}/notice/\d+/",
    f"{CLIENT_V1_1_0_PREFIX}/notice/status/"
]


class LoginAuth(BaseAuthentication):

    def authenticate_header(self, request):
        """
        获取验证auth
        @param request:
        @return:
        """

        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if not auth:
            raise AuthenticationFailed('Login is required!')
        return auth

    def authenticate(self, request):
        # 拿token
        _, token = self.authenticate_header(request).split()
        # 去缓存看看有没有
        info = token_2_user_info(token)
        if not info:
            raise AuthenticationFailed("请登录")
        # 查询缓存
        user = cache.get("UserInfo:"+str(info.get("user_id")))
        if not user:
            try:
                user = UserModel.objects.using("credible_data").get(pk=info.get("user_id"))
                cache.set("UserInfo:"+str(user.id), user, NORMAL_CACHE_TIME*6)
            except UserModel.DoesNotExist:
                raise AuthenticationFailed('Invalid token.')

        if hasattr(request, "company"):
            company = request.company
            exists = cache.get(f"S1UserCompanyMap:{company.id}|{user.id}")
            if not exists:
                # 检查企业与用户关系
                exists = S1UserCompanyMap.objects.filter(
                    s1_user_id=user.id,
                    company_id=company.id,
                    # is_deleted=False
                ).exists()
                cache.set(f"S1UserCompanyMap:{company.id}|{user.id}", exists, NORMAL_CACHE_TIME)
            if not exists:
                raise APIException("当前用户与当前企业无关联关系")
            if not any(map(lambda x: re.match(x, request.path), ALL_COMPANY_PATH)):
                if not CompanyReviewLog.objects.filter(company_id=company.id, status="pass").exists():
                    raise APIException("当前企业审核未通过")
        # 检查企业与用户关系
        if (not user.is_active) or user.is_deleted:
            raise AuthenticationFailed("该账户已被冻结")

        if scf_config["enable"]:
            resp = s1_application_open(token)
            if resp.get("code") != status.HTTP_200_OK:
                raise AuthenticationFailed("无服务权限")
            # 如果url是管理端接口, 需要校验一系列规则:
            if re.match(MANAGEMENT_PATH_PREFIX, request.path):
                # 如果当前用户在供应链金融没有角色，并且也不是s1企业的创建者。
                """
                用户第一次进入供应链金融系统时, 肯定是没有角色的.所以需要去s1查询当前用户是否为企业的创建人
                """
                if not UserRole.objects.filter(s1_user_id=user.id).exists():
                    is_root_user = Company.objects.using("credible_data").filter(
                        pk=scf_config["company"],
                        # s1_user_id=user.root_s1_user_id
                        s1_user_id=user.id
                    ).exists()
                    if not is_root_user:
                        raise AuthenticationFailed("无服务权限")

            # 不是管理端接口, 只要需要看企业是否有未到期的服务即可(s1_application_open实现了这个功能)
            start = resp.get("data").get("service_start")
            end = resp.get("data").get("service_end")
            now = str(datetime.datetime.now())
            if now < start or now > end:
                raise AuthenticationFailed("无服务权限")
        return user, token
