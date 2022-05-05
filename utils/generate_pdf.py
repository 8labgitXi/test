# -*- coding: utf-8 -*-
"""
@File        : generate_pdf.py
@Author      : niuxingjie
@Time        : 2022/4/13 15:42
@Description :
    1. 使用的生成pdf的第三方包：weasyprint
        - [系统依赖](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#linux)
        - [python-api](https://doc.courtbouillon.org/weasyprint/stable/api_reference.html#python-api)
        - [Fonts](https://doc.courtbouillon.org/weasyprint/stable/api_reference.html#fonts)
            - 系统需要安装好合适的中文字体（Ubuntu可以用apt-get install ttf-wqy-microhei）
"""
import weasyprint


def generate_pdf_from_html(html, filename=None):
    """
    html源代码生成pdf文件

    @param html: html源代码
    @param filename: pdf文件名（路径）
    @return:
        - filename为None时，返回bytes类型的文件内容对象
        - filename为文件名时，生成文件，返回None
    """
    wp = weasyprint.HTML(string=html, encoding='utf-8')
    return wp.write_pdf(filename)

