# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import json
from django import template
import logging
from uuid import uuid4

from events.models import Query
from events.util import resolve

register = template.Library()

@register.inclusion_tag('events/query-table.html', takes_context=True)
def query_table(context, query_string, form=None, **kwargs):
    log = logging.getLogger(__name__)
    log.debug(f"Received {query_string=}")
    ctx = {}
    if form and form.is_valid():
        log.debug(f"Form is valid: {form.cleaned_data}")
        ctx = form.cleaned_data
    else:
        log.debug(f"Form is not valid: {form.errors}")
        ctx = {}
    if kwargs:
        log.debug(f"kwargs: {kwargs}")
        ctx.update(kwargs)
    query_obj = Query(text=query_string)
    log.debug(f"Query object: {query_obj}")
    results = query_obj.resolve(request=context["request"], context=ctx)
    results = resolve(results)
    if results:
        fields = [key for key in results[0].keys()]
    else:
        fields = []
    return {
        "fields": fields,
        "results": results,
    }

@register.inclusion_tag('events/query-chart.html', takes_context=True)
def query_chart(context, query_string, form=None, **kwargs):
    log = logging.getLogger(__name__)
    log.debug(f"Received {query_string=}")
    if form and form.is_valid():
        log.debug(f"Form is valid: {form.cleaned_data}")
        ctx = form.cleaned_data
    else:
        log.debug(f"Form is not valid: {form.errors}")
        ctx = {}
    if kwargs:
        log.debug(f"kwargs: {kwargs}")
        ctx.update(kwargs)
    query_obj = Query(text=query_string)
    log.debug(f"Query object: {query_obj}")
    results = query_obj.resolve(request=context["request"], context=ctx)
    try:
        results = resolve(results)[0]
    except KeyError:
        pass

    return {
        "results": results,
        "id": uuid4(),
    }

@register.simple_tag()
def query_table_js():
    return '/static/js/fl-table.js'

@register.simple_tag()
def query_chart_js():
    return '/static/js/fl-chart.js'

@register.filter(name='lookup')
def lookup(value, arg):
    return value[arg]