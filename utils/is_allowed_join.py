# -*- coding: utf-8 -*-
"""
@File        : is_allowed_join.py
@Author      : yu wen yang
@Time        : 2022/3/30 10:16 上午
@Description :
"""
import jsonpath
from django.db import transaction

from client.models.menus import RoleAppMenus, AppMenus
from client.models.role import UserRole, Role
from consts.user import FOUNDER_NAME, NOTICE_NAME, MESSAGE_CODES
from utils.get_s1_application_open import s1_application_open
from utils.permission_menu import get_permission_menu


def is_had_permission(user_id, platform_id, token=None):
    """

    @param user_id: 用户id
    @param platform_id: 平台id
    @param token: token
    @return:
    """
    """
    查询当前用户是否是s1企业的创建人, 并且企业在s1是否购买应用
    """
    # 如果有token, 则不是从供应链金融管理端登录, 查看该用户的企业是否有未到期的供应链金融服务
    if token:
        resp = s1_application_open(token)
        if resp.get("code") != 200:
            return
    # 查询当前用户有没有绑定角色
    user_founder_is_exists = UserRole.objects.filter(
        s1_user_id=user_id,
        role__platform_id=platform_id
    ).exists()

    with transaction.atomic():
        # 当前用户没有绑定创建者角色, 查询有没有创建者这个角色
        if not user_founder_is_exists:
            role_instance = Role.objects.filter(
                name=FOUNDER_NAME,
                platform_id=platform_id
            ).first()
            # 如果也没有创建者个角色, 先创建创建者角色, 把用户和角色关联;如果有创建者角色, 直接关联.
            if not role_instance:
                role_instance = Role.objects.create(
                    name=FOUNDER_NAME,
                    desc=FOUNDER_NAME,
                    platform_id=platform_id,
                    disable=False
                )
                # 获取到全部权限
                all_menus = get_permission_menu(platform_id, list())
                # 取出第三级菜单
                role_ids = jsonpath.jsonpath(all_menus, "$.[*].children.*.children.*.id")

                for i in role_ids:
                    RoleAppMenus.objects.create(
                        role=role_instance,
                        app_menus_id=i
                    )

            notice_role_instance = Role.objects.filter(
                name=NOTICE_NAME,
                platform_id=platform_id
            ).first()

            # 如果没有消息管理员角色
            if not notice_role_instance:
                notice_role_instance = Role.objects.create(
                    name=NOTICE_NAME,
                    desc=NOTICE_NAME,
                    platform_id=platform_id,
                    disable=False
                )
                # 获取消息相关的权限
                notice_menu_ids = AppMenus.objects.filter(
                    code__in=MESSAGE_CODES,
                    is_deleted=False
                ).values_list("id", flat=True)

                # 创建消息相关的权限
                notice_list = [
                    RoleAppMenus(
                        role=notice_role_instance,
                        app_menus_id=menu_id
                    ) for menu_id in notice_menu_ids
                ]
                RoleAppMenus.objects.bulk_create(notice_list)

            user_roles = [
                UserRole(s1_user_id=user_id, role=role_instance),
                UserRole(s1_user_id=user_id, role=notice_role_instance)
            ]
            UserRole.objects.bulk_create(user_roles)

    return True
