#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
import os
import urllib

import flask
from flask import Flask
import requests

app = Flask(__name__)

# User configuration variables are added to the Flask config.
# To set them, either specify a python config file for all your Flask
# settings...
ENV_SETTINGS_PATH = 'TOGGLR_SETTINGS'
if ENV_SETTINGS_PATH in os.environ:
    app.config.from_envvar(ENV_SETTINGS_PATH)

# ...or use environment variables for Togglr-specific values.
ENV_CONFIG_VARS = dict(
    api_token='TOGGLR_TOGGL_API_TOKEN',
    wsid='TOGGLR_TOGGL_WSID',
)
for var in ENV_CONFIG_VARS.values():
    if var in os.environ:
        app.config[var] = os.environ[var]


def _config_warning():
    for var in sorted(ENV_CONFIG_VARS.values()):
        if var not in app.config:
            msg = 'Warning: configuration variable %s not defined' % var
            app.logger.warn(msg)


class TogglServerError(Exception):
    pass


class TogglWeekly(object):

    def __init__(self, api_token, wsid, day_in_week=None, calculate='time'):
        self.api_token = api_token
        self.wsid = wsid
        self.url = 'https://toggl.com/reports/api/v2/weekly'
        self.day_in_week = day_in_week if day_in_week else datetime.date.today()
        self.calculate = calculate

    def get_dates(self):
        today = self.day_in_week
        start_week = today - datetime.timedelta(days=today.weekday())
        end_week = start_week + datetime.timedelta(days=6)
        return (start_week, end_week)

    def format_date(self, date):
        return date.strftime('%Y-%m-%d')

    def build_url(self, since, until):
        params = {
            'user_agent': 'testing',
            'workspace_id': self.wsid,
            'since': since,
            'until': until,
            'calculate': self.calculate,
        }
        return self.url + '?' + urllib.urlencode(params)

    def fetch(self):
        since, until = self.get_dates()
        since = self.format_date(since)
        until = self.format_date(until)
        headers = {'content-type': 'application/json'}
        auth = requests.auth.HTTPBasicAuth(self.api_token, 'api_token')
        url = self.build_url(since, until)
        r = requests.get(url, headers=headers, auth=auth)
        data = r.json()
        if r.status_code != 200:
            msg = '%d. ' % r.status_code
            if 'error' in data:
                msg += '. '.join([data['error']['message'],
                                  data['error']['tip']])
            else:
                msg += r.reason
            raise TogglServerError(msg)
        return data

    def earnings(self):
        report = self.fetch()
        if report['week_totals']:
            earnings = report['week_totals'][0]['amount'][-1]
            return earnings or 0
        return 0

    def billable(self):
        report = self.fetch()
        return report['total_billable'] or 0


def ms_to_hours(ms):
    return (ms / 1000) / 3600


def format_ms_to_hours_minutes(ms):
    s = ms / 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return '{0}h{1}m'.format(h, m)


def build_item_for_number_widget(value, text=None, prefix=None, value_type=None):
    return {
        "value": value,
        "text": text,
        "prefix": prefix,
        "type": value_type,
    }


def build_content_for_number_widget(items):
    content = {
        "item": items
    }
    return content


@app.route("/")
def total_billable_this_week():
    api_token = app.config[ENV_CONFIG_VARS['api_token']]
    wsid = app.config[ENV_CONFIG_VARS['wsid']]

    w_this_week = TogglWeekly(api_token, wsid)
    w_last_week = TogglWeekly(
        api_token, wsid, day_in_week=datetime.date.today() - datetime.timedelta(days=7))
    billable_hours_this_week = ms_to_hours(w_this_week.billable())
    billable_hours_last_week = ms_to_hours(w_last_week.billable())
    item_this_week = build_item_for_number_widget(billable_hours_this_week)
    item_last_week = build_item_for_number_widget(billable_hours_last_week)
    content = build_content_for_number_widget([item_this_week, item_last_week])
    return flask.jsonify(**content)


@app.route("/resources-week")
def resources_invested_this_week():
    api_token = app.config[ENV_CONFIG_VARS['api_token']]
    wsid = app.config[ENV_CONFIG_VARS['wsid']]

    seven_days_ago = datetime.date.today() - datetime.timedelta(days=7)
    w_this_week = TogglWeekly(api_token, wsid, calculate='earnings')
    w_last_week = TogglWeekly(
        api_token, wsid, seven_days_ago, calculate='earnings')
    resources_this_week = w_this_week.earnings()
    resources_last_week = w_last_week.earnings()
    item_this_week = build_item_for_number_widget(
        resources_this_week, prefix='£')
    item_last_week = build_item_for_number_widget(
        resources_last_week, prefix='£')
    content = build_content_for_number_widget([item_this_week, item_last_week])
    return flask.jsonify(**content)


if __name__ == "__main__":
    _config_warning()
    app.run(debug=True)
