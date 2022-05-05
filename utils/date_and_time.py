# -*- coding: utf-8 -*-
"""
@File        : date_and_time.py
@Author      : niuxingjie
@Time        : 2022/3/7 11:23
@Description :
"""
import arrow
import datetime
import calendar

from consts.common import DATE_FORMAT


def n_years_later(start, years):
    """
    计算start时间years年后的时间:
        - 闰年2月29日在非闰年会变成2月28日
    """
    try:
        end = start.replace(start.year + years)
    except ValueError:
        end = start.replace(start.year + years, day=28)
    return end


def n_months_later(start, months):
    """
    计算start时间months月后的时间:
        - 某月的31日不存在时，会变成次月的最后一天
    """
    start = arrow.get(start)
    end = start.shift(months=+months)
    return end


def n_days_later(start, days):
    """
    计算start时间days天后的时间
    """
    timedelta = datetime.timedelta(days=days)
    end = start + timedelta
    return end


def n_hours_later(start, hours):
    """
    计算start时间hours小时后的时间
    """
    start = arrow.get(start)
    end = start.shift(hours=+hours)
    return end


def n_minutes_later(start, mins):
    """
    计算start时间mins分钟后的时间
    """
    timedelta = datetime.timedelta(minutes=mins)
    end = start + timedelta
    return end


def get_period(month):
    """获取月份的开始日期和结束日期

    @param month: 月份，如 2022-04
    @return: 此月的开始日期和结束日期，如（2022-04-01, 2022-04-31）
    """
    dt = datetime.datetime.strptime(month, DATE_FORMAT)
    week_days, month_days = calendar.monthrange(dt.year, dt.month)
    start_day = datetime.date(dt.year, dt.month, day=1)
    end_day = datetime.date(dt.year, dt.month, day=month_days)
    return start_day, end_day
