#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
import os

import flask
from flask import Flask

from toggl_api import TogglWeekly
import geckoboard
import utils

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


@app.route("/")
def total_billable_this_week():
    api_token = app.config[ENV_CONFIG_VARS['api_token']]
    wsid = app.config[ENV_CONFIG_VARS['wsid']]

    seven_days_ago = datetime.date.today() - datetime.timedelta(days=7)
    w_this_week = TogglWeekly(api_token, wsid)
    w_last_week = TogglWeekly(api_token, wsid, seven_days_ago)

    billable_hours_this_week = utils.ms_to_hours(w_this_week.billable())
    billable_hours_last_week = utils.ms_to_hours(w_last_week.billable())
    item_this_week = geckoboard.build_item_for_number_widget(billable_hours_this_week)
    item_last_week = geckoboard.build_item_for_number_widget(billable_hours_last_week)

    items = [item_this_week, item_last_week]
    content = geckoboard.build_content_for_number_widget(items)
    return flask.jsonify(**content)


@app.route("/resources-week")
def resources_invested_this_week():
    api_token = app.config[ENV_CONFIG_VARS['api_token']]
    wsid = app.config[ENV_CONFIG_VARS['wsid']]

    seven_days_ago = datetime.date.today() - datetime.timedelta(days=7)
    w_this_week = TogglWeekly(api_token, wsid, calculate='earnings')
    w_last_week = TogglWeekly(api_token, wsid, seven_days_ago, calculate='earnings')

    resources_this_week = w_this_week.earnings()
    resources_last_week = w_last_week.earnings()
    item_this_week = geckoboard.build_item_for_number_widget(
        resources_this_week, prefix='£')
    item_last_week = geckoboard.build_item_for_number_widget(
        resources_last_week, prefix='£')

    items = [item_this_week, item_last_week]
    content = geckoboard.build_content_for_number_widget(items)
    return flask.jsonify(**content)


if __name__ == "__main__":
    _config_warning()
    app.run(debug=True)
