#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
import os

import flask
from flask import Flask

from config import TOGGLR_CONFIG
from toggl_api import TogglWeekly
import geckoboard
import utils

app = Flask(__name__)
app.config.update(TOGGLR_CONFIG)
TOGGLR_CONFIG.check_and_warn(app.logger)


@app.route("/")
def total_billable_this_week():
    seven_days_ago = datetime.date.today() - datetime.timedelta(days=7)
    w_this_week = TogglWeekly()
    w_last_week = TogglWeekly(date=seven_days_ago)

    billable_hours_this_week = utils.ms_to_hours(w_this_week.billable())
    billable_hours_last_week = utils.ms_to_hours(w_last_week.billable())
    item_this_week = geckoboard.build_item_for_number_widget(billable_hours_this_week)
    item_last_week = geckoboard.build_item_for_number_widget(billable_hours_last_week)

    items = [item_this_week, item_last_week]
    content = geckoboard.build_content_for_number_widget(items)
    return flask.jsonify(**content)


@app.route("/resources-week")
def resources_invested_this_week():
    seven_days_ago = datetime.date.today() - datetime.timedelta(days=7)
    w_this_week = TogglWeekly(calculate='earnings')
    w_last_week = TogglWeekly(date=seven_days_ago, calculate='earnings')

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
    app.run()
