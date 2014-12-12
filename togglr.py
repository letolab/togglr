#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import datetime

import flask
from flask import Flask
import requests

app = Flask(__name__)


class Weekly(object):

    def __init__(self, calculate='time'):
        self.api_token='10ca7619f6ade0f7769adc6ff55af416'
        self.wsid = 737293
        self.url = 'https://toggl.com/reports/api/v2/weekly'
        self.calculate = calculate

    def get_dates(self):
        today = datetime.date.today()
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
    return '{0} h {1} min'.format(h, m)


def build_content_for_number_widget(value, text, prefix=None):
    content = {
        "item": [
            {
                "value": value,
                "text": text,
                "prefix": prefix,
            }
        ]
    }
    return content


@app.route("/")
def total_billable_this_week():
    w = Weekly()
    billable_hours = ms_to_hours(w.billable())
    content = build_content_for_number_widget(billable_hours, 'Billable hours this week')
    return flask.jsonify(**content)


@app.route("/revenue-week")
def resources_invested_this_week():
    w = Weekly(calculate='earnings')
    estimated_revenue = w.earnings()
    content = build_content_for_number_widget(estimated_revenue, 'Resources invested this week', prefix='£')
    return flask.jsonify(**content)


if __name__ == "__main__":
    app.run(debug=True)
