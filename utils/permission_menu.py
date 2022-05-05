# -*- coding: utf-8 -*-
"""
@File        : permission_menu.py
@Author      : yu wen yang
@Time        : 2022/3/8 10:06 上午
@Description :
"""
import json

from client.models.menus import AppMenus
from management.serializers.roles import PermissionSerializer


def get_permission_menu(platform_id, selected_list, first_menu_obj=None, is_all=False):
    """
    获取权限菜单
    使用方法:
        如果需要获取全部权限,
    @param platform_id: 平台id
    @param first_menu_obj: 一级菜单的queryset(区分详情页和登录后的权限菜单, 通过一级菜单查询到后面子级的菜单.)
    @param selected_list: 选中权限的列表  ["code1", "code2"]
    @param is_all: 是否获取全部权限(区分详情页和登录后的权限.详情页返回全部权限, 登录后只返回用户角色对应的权限)
    @return:
    """
    if not first_menu_obj:
        is_all = True
        # 获取一级菜单, 如果接口没有传过来一级菜单的事例, 那么就获取全部path为空的
        first_menu_obj = AppMenus.objects.filter(
            path=list(),
            platform_id=platform_id
        ).order_by("-id")
    first_menu_permission_serializer = PermissionSerializer(first_menu_obj, many=True)
    # 循环一级菜单
    for first_menu in first_menu_permission_serializer.data:
        # 判断当前权限有没有被选中
        first_menu["is_selected"] = first_menu["code"] in selected_list
        # 通过一级菜单code查询到一级菜单下的所有二级菜单
        second_menu_permissions = AppMenus.objects.filter(
            path=[first_menu["code"]],
            platform_id=platform_id
        ).order_by("-id")
        second_menu_permission_serializer = PermissionSerializer(second_menu_permissions, many=True)
        # 将二级菜单加入到一级菜单子级中
        second_menu_permission_serializer_data = json.loads(json.dumps(second_menu_permission_serializer.data))
        first_menu["children"] = second_menu_permission_serializer_data
        # 循环二级菜单
        for second_menu in second_menu_permission_serializer_data[::-1]:
            second_menu["is_selected"] = second_menu["code"] in selected_list
            # 判断如果二级菜单的code没有在已选中的权限中, 并且不是获取全部权限, 将这个二级菜单删掉.开始下次循环
            if (second_menu["code"] not in selected_list) and (not is_all):
                second_menu_permission_serializer_data.remove(second_menu)
                continue
            # 通过一级菜单code和二级菜单code查询到三级菜单
            three_menu_permissions = AppMenus.objects.filter(
                path=[first_menu["code"], second_menu["code"]],
                platform_id=platform_id
            ).order_by("-id")
            three_menu_permission_serializer = PermissionSerializer(three_menu_permissions, many=True)
            # 把二级菜单下的三级菜单加到二级菜单中
            three_menu_permission_serializer_data = json.loads(json.dumps(three_menu_permission_serializer.data))
            second_menu["children"] = three_menu_permission_serializer_data
            for three_menu in three_menu_permission_serializer_data[::-1]:
                three_menu["is_selected"] = three_menu["code"] in selected_list
                if (three_menu["code"] not in selected_list) and (not is_all):
                    three_menu_permission_serializer_data.remove(three_menu)
                    continue

    return first_menu_permission_serializer.data
