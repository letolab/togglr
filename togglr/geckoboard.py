# -*- coding: utf-8 -*-

# Functions relating to Geckoboard API


def build_item_for_number_widget(value, text=None, prefix=None, value_type=None):
    return {
        "value": value,
        "text": text,
        "prefix": prefix,
        "type": value_type,
    }


def build_content_for_number_widget(items):
    # First item is primary metric, second item is optional comparison metric.
    content = {
        "item": items
    }
    return content
