# -*- coding: utf-8 -*-
"""
@File        : oss_util.py
@Author      : liuda
@Time        : 2021/9/29 11:24
@Description :
    注意：
        - 阿里云oss在同一文件夹下使用put_object上传相同的文件，会直接覆盖已有文件。
"""
import os

import oss2
from rest_framework import status

from scf_project import settings

access_id = settings.oss_config.get("access_id")
access_key = settings.oss_config.get("access_key")
bucket_name = settings.oss_config.get("bucket_name")
endpoint = settings.oss_config.get("endpoint")


def upload_oss_file(file_name: str, file_folder: str, content: str, flag=False) -> str:
    """
    上传文件到OSS
    @param file_name:   上传到oss的文件名
    @param file_folder: 上传到oss的文件路径
    @param content:     文件内容
    @return:            oss的URL
    """

    auth = oss2.Auth(access_id, access_key)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    # 上传
    file_path = os.path.join(file_folder, file_name)
    if flag:
        result = bucket.put_object_from_file(file_path, content)  # 上传一个本地文件到OSS的普通文件
    else:
        result = bucket.put_object(file_path, content)

    # 返回的URL
    if result.status == status.HTTP_200_OK:
        url = result.resp.response.url
        return url
    else:
        return None


if __name__ == '__main__':
    url = upload_oss_file("test.txt", "test", "哈哈")
    print(url)
