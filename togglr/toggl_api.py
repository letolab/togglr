# -*- coding: utf-8 -*-
import datetime
import urllib

import requests

import utils


class TogglServerError(Exception):
    pass


class TogglWeekly(object):

    def __init__(self, api_token, wsid, date=None, calculate='time'):
        """ Fetch seven-day durations or earnings report from Toggl API.

        - api_token:    Toggl API token
        - wsid:         Toggl workspace ID
        - date:         Datetime object. Report will be returned for the week
                        in which this date occurs.
        - calculate:    'time' (to report durations) or 'earnings'.
        """
        self.api_token = api_token
        self.wsid = wsid
        self.calculate = calculate
        self.given_date = date if date else datetime.date.today()

        self.url = 'https://toggl.com/reports/api/v2/weekly'
        self.starting_date = utils.get_first_day_of_week_for_date(self.given_date)
        self.ending_date = self.starting_date + datetime.timedelta(days=6)

    def _format_date(self, date):
        return date.strftime('%Y-%m-%d')

    def _build_url(self):
        # According to documentation the weekly API doesn't accept an 'until'
        # param, so self.ending_date isn't strictly necessary.
        params = {
            'user_agent': 'testing',
            'workspace_id': self.wsid,
            'since': self._format_date(self.starting_date),
            'until': self._format_date(self.ending_date),
            'calculate': self.calculate,
        }
        return self.url + '?' + urllib.urlencode(params)

    def fetch(self):
        headers = {'content-type': 'application/json'}
        auth = requests.auth.HTTPBasicAuth(self.api_token, 'api_token')
        url = self._build_url()
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
