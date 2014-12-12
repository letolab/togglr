#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import datetime
import os

import flask
from flask import Flask
import requests

app = Flask(__name__)
API_TOKEN = os.environ.get('API_TOKEN')
WSID = os.environ.get('WSID')


class Weekly(object):

    def __init__(self, day_in_week=None, calculate='time'):
        self.api_token = API_TOKEN
        self.wsid = WSID
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
        params = '?workspace_id={wsid}&since={since}&until={until}&user_agent=testing&calculate={calculate}'.format(
            wsid=self.wsid,
            since=since,
            until=until,
            calculate=self.calculate,
        )
        return self.url + params

    def fetch(self):
        since, until = self.get_dates()
        since = self.format_date(since)
        until = self.format_date(until)
        headers = {'content-type': 'application/json'}
        auth = requests.auth.HTTPBasicAuth(self.api_token, 'api_token')
        url = self.build_url(since, until)
        r = requests.get(url, headers=headers, auth=auth)
        return json.loads(r.content)

    def earnings(self):
        report = self.fetch()
        return report['week_totals'][0]['amount'][-1]

    def billable(self):
        report = self.fetch()
        return report['total_billable']


def ms_to_hours(ms):
    return (ms/1000)/3600


def format_ms_to_hours_minutes(ms):
    s = ms/1000
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
    w_this_week = Weekly()
    w_last_week = Weekly(day_in_week=datetime.date.today() - datetime.timedelta(days=7))
    billable_hours_this_week = ms_to_hours(w_this_week.billable())
    billable_hours_last_week = ms_to_hours(w_last_week.billable())
    item_this_week = build_item_for_number_widget(billable_hours_this_week)
    item_last_week = build_item_for_number_widget(billable_hours_last_week)
    content = build_content_for_number_widget([item_this_week, item_last_week])
    return flask.jsonify(**content)


@app.route("/resources-week")
def resources_invested_this_week():
    w_this_week = Weekly(calculate='earnings')
    w_last_week = Weekly(day_in_week=datetime.date.today() - datetime.timedelta(days=7), calculate='earnings')
    resources_this_week = w_this_week.earnings()
    resources_last_week = w_last_week.earnings()
    item_this_week = build_item_for_number_widget(resources_this_week, prefix='£')
    item_last_week = build_item_for_number_widget(resources_last_week, prefix='£')
    content = build_content_for_number_widget([item_this_week, item_last_week])
    return flask.jsonify(**content)


if __name__ == "__main__":
    app.run(debug=True)
