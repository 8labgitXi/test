# -*- coding: UTF-8 -*-
"""
@Summary : docstr
@Author  : Rey
@Time    : 2022-04-06 09:48:38
"""
from notice.helpers import BaseGetAllowedTypes


class ScfGetAllowedViewTypes(BaseGetAllowedTypes):
    def __init__(self, receiver, company_type) -> None:
        super().__init__()
        self.receiver = receiver
        self.company_type = company_type

    def judge_notice_types(self) -> list:
        allowed_notice_type_ids = []

        self.done_notice_type.append('system')
        allowed_notice_type_ids.append(self.all_notice_type_names['system'])

        return allowed_notice_type_ids

    def judge_notice_receiver_types(self) -> list:
        allowed_receiver_type_ids = []

        self.done_receiver_type.append('core')
        if self.company_type == 'core':
            allowed_receiver_type_ids.append(self.all_receiver_type_names['core'])

        self.done_receiver_type.append('normal')
        if self.company_type == 'normal':
            allowed_receiver_type_ids.append(self.all_receiver_type_names['normal'])

        self.done_receiver_type.append('financial_institutions')
        if self.company_type == 'financial_institutions':
            allowed_receiver_type_ids.append(self.all_receiver_type_names['financial_institutions'])

        return allowed_receiver_type_ids
