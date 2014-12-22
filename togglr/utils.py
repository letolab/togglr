# -*- coding: utf-8 -*-
import datetime


def get_first_day_of_week_for_date(date):
    # Week starts Monday
    return date - datetime.timedelta(days=date.weekday())


def ms_to_hours(ms):
    return (ms / 1000) / 3600


def ms_to_hours_minutes(ms):
    s = ms / 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return '{0}h{1}m'.format(h, m)
