#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import json

from mock import patch
import mock

from togglr import togglr


class TogglResponseExample(object):
    # Example response data adapted from
    # https://github.com/toggl/toggl_api_docs/blob/d75f782c25ff0f57710b8ae3ae08945f486acc9f/reports/weekly.md

    @staticmethod
    def time():
        return {
            'total_grand': 36004000,
            'total_billable': 14400000,
            'total_currencies': [{'currency': 'EUR', 'amount': 40.00}],
            'week_totals': [None, None, 14401000, 7203000, 14400000, None, None, 36004000],
            'data': [
                {
                    'title': {'project': 'Toggl Desktop', 'client': 'Toggl'},
                    'pid': 7363449,
                    'totals': [None, None, None, None, 14400000, None, None, 14400000],
                    'details':[
                        {
                            'uid': 352243,
                            'title': {'user': 'John Swift'},
                            'totals': [None, None, None, None, 14400000, None, None, 14400000]
                        }
                    ]
                }, {
                    'title': {'project': 'Important Client', 'client': None},
                    'pid': 1651,
                    'totals': [None, None, 14400000, None, None, None, None, 14400000],
                    'details':[
                        {
                            'uid': 31232243,
                            'title': {'user': 'Jane Doe'},
                            'totals': [None, None, 14400000, None, None, None, None, 14400000]
                        }
                    ]
                }, {
                    'title': {'project': None, 'client': None},
                    'pid': None,
                    'totals': [None, None, 1000, 7203000, None, None, None, 7204000],
                    'details':[
                        {
                            'uid': 19569,
                            'title': {'user': 'John Swift'},
                            'totals': [None, None, 1000, 7203000, None, None, None, 7204000]
                        }
                    ]
                }
            ],
        }

    @staticmethod
    def earnings():
        return {
            'total_grand': 36004000,
            'total_billable': 14400000,
            'total_currencies': [{'currency': 'EUR', 'amount': 40.00}],
            'week_totals': [
                {
                    'currency': 'EUR',
                    # TODO - when does Toggl return '0' rather than None?
                    # Do the two values need to be handled separately?
                    'amount': [None, None, 0, None, 40, None, None, 40],
                },
            ],
            'data': [
                {
                    'title': {'project': 'Toggl Desktop', 'client': 'Toggl'},
                    'pid': 7363449,
                    'totals': [
                        {
                            'currency': 'EUR',
                            'amount': [None, None, 0, None, 0, None, None, 0],
                        }
                    ],
                    'details':[
                        {
                            'uid': 352243,
                            'title': {'user': 'John Swift'},
                            'totals': [
                                {
                                    'currency': 'EUR',
                                    'amount': [None, None, 0, None, 40, None, None, 40],
                                }
                            ]
                        }
                    ]
                }, {
                    'title': {'project': 'Important Client', 'client': None},
                    'pid': 1651,
                    'totals': [
                        {
                            'currency': 'EUR',
                            'amount': [None, None, 0, None, 0, None, None, 0],
                        }
                    ],
                    'details':[
                        {
                            'uid': 31232243,
                            'title': {'user': 'Jane Doe'},
                            'totals': [
                                {
                                    'currency': 'EUR',
                                    'amount': [None, None, 0, None, 0, None, None, 0],
                                }
                            ]
                        }
                    ]
                }, {
                    'title': {'project': None, 'client': None},
                    'pid': None,
                    'totals': [
                        {
                            'currency': 'EUR',
                            'amount': [None, None, 0, None, 0, None, None, 0],
                        }
                    ],
                    'details':[
                        {
                            'uid': 19569,
                            'title': {'user': 'John Swift'},
                            'totals': [
                                {
                                    'currency': 'EUR',
                                    'amount': [None, None, 0, None, 0, None, None, 0],
                                }
                            ]
                        }
                    ]
                }
            ],
        }

    @staticmethod
    def error():
        return {
            'error': {
                'message': 'We are sorry, this Error should never happen to you',
                'tip': 'Please contact support@toggl.com with information on your request',
                'code': 500
            }
        }


class TestEndpoints(unittest.TestCase):

    def setUp(self):
        togglr.app.config['TESTING'] = True
        self.app = togglr.app.test_client()

    def tearDown(self):
        mock.patch.stopall()

    def _get_json_response(self, url):
        return json.loads(self.app.get(url).data)

    def _add_requests_api(self, get, return_value, status_code=200):
        mock_resp = mock.Mock()
        mock_resp.json = mock.Mock(return_value=return_value)
        mock_resp.status_code = status_code
        mock_resp.reason = 'foo'
        get.return_value = mock_resp

    @patch('requests.get')
    def test_billable(self, get):
        hours = 15
        ms_in_hour = 3600000

        resp = TogglResponseExample.time()
        resp['total_billable'] = hours * ms_in_hour
        self._add_requests_api(get, resp)

        data = self._get_json_response('/')
        self.assertEqual(data['item'][0]['value'], hours)
        self.assertEqual(data['item'][1]['value'], hours)

    @patch('requests.get')
    def test_resources(self, get):
        earnings = 100
        resp = TogglResponseExample.earnings()
        resp['week_totals'][0]['amount'][-1] = earnings
        self._add_requests_api(get, resp)

        data = self._get_json_response('/resources-week')
        self.assertEqual(data['item'][0]['value'], earnings)
        self.assertEqual(data['item'][1]['value'], earnings)

    @patch('requests.get')
    def test_billable_total_is_none(self, get):
        resp = TogglResponseExample.time()
        resp['total_billable'] = None
        self._add_requests_api(get, resp)

        data = self._get_json_response('/')
        self.assertEqual(data['item'][0]['value'], 0)
        self.assertEqual(data['item'][1]['value'], 0)

    @patch('requests.get')
    def test_earnings_total_is_none(self, get):
        resp = TogglResponseExample.earnings()
        resp['week_totals'][0]['amount'][-1] = None
        self._add_requests_api(get, resp)

        data = self._get_json_response('/resources-week')
        self.assertEqual(data['item'][0]['value'], 0)
        self.assertEqual(data['item'][1]['value'], 0)


if __name__ == "__main__":
    unittest.main()
