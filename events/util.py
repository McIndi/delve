# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import sys
import ast
import logging
import inspect
from io import StringIO
from itertools import chain
from types import GeneratorType
from collections.abc import Mapping
import django.core.exceptions
from django.utils.timezone import get_current_timezone

from django.db.models.query import (
    QuerySet,
    ValuesIterable,
)
from django.conf import settings
from django.utils import timezone
import pytz

from django.db.models import Model
from django.forms.models import model_to_dict

def deep_update(d, u, depth=-1):
    """
    Recursively merge or update dict-like objects. 
    >>> update({'k1': {'k2': 2}}, {'k1': {'k2': {'k3': 3}}, 'k4': 4})
    {'k1': {'k2': {'k3': 3}}, 'k4': 4}
    """
    for k, v in u.items():
        if isinstance(v, Mapping) and not depth == 0:
            r = deep_update(d.get(k, {}), v, depth=max(depth - 1, -1))
            d[k] = r
        elif isinstance(d, Mapping):
            d[k] = u[k]
        else:
            d = {k: u[k]}
    return d


def run_query(id, **kwargs):
    from events.models import Query
    try:
        query = Query.objects.get(pk=id)
    except (Query.DoesNotExist, django.core.exceptions.ValidationError):
        try:
            query = Query.objects.get(name=id)
        except Query.DoesNotExist:
            query = Query(text=id)
    class fake_request:
        user = query.user
    events = query.resolve(request=fake_request, context=kwargs)
    return events


def cast(value):
    try:
        return ast.literal_eval(value)
    except SyntaxError:
        try:
            from dateutil.parser import parse
            return parse(value)
        except ValueError:
            return value
    except ValueError:
        return value

def is_results(data):
    if isinstance(data, GeneratorType) or inspect.isgeneratorfunction(data) or isinstance(data, list) or isinstance(data, QuerySet):
        return True
    return False

def ensure_list(data):
    if isinstance(data, GeneratorType) or inspect.isgeneratorfunction(data):
        return list(data)
    elif isinstance(data, QuerySet):
        return list(data.values())
    elif isinstance(data, list):
        return data
    else:
        raise ValueError(f"Cannot convert {type(data)} to list.")
    
def custom_model_to_dict(instance):
    """
    Convert a model instance to a dictionary, including all fields.
    """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        data[f.name] = f.value_from_object(instance)
    return data

user_tz = pytz.timezone(settings.TIME_ZONE)
def localize_datetimes(obj):
    for key, value in obj.items():
        if isinstance(value, timezone.datetime):
            if timezone.is_naive(value):
                value = timezone.make_aware(value, get_current_timezone())
            obj[key] = value.astimezone(user_tz)
    return obj

def resolve(events):
    from events.models import BaseEvent
    log = logging.getLogger(__name__)
    # if isinstance(events, QuerySet):
    #     log.debug(f"Casting matching events, detected {type(events)}")
    #     events = list(events.values())
    if hasattr(events, "_iterable_class") and events._iterable_class == ValuesIterable:
        log.debug(f"Casting matching events, detected {type(events)}")
        # log.info(f"Found {type(events)=}")
        events = list(events)
    elif isinstance(events, Model):
        log.debug(f"Casting matching events, detected {type(events)}")
        # log.info(f"Found {type(events)=}")
        # events = events.as_dict()
        events = custom_model_to_dict(events)
    elif isinstance(events, QuerySet):
        log.debug(f"Casting matching events, detected {type(events)}")
        log.info(f"Found {type(events)=}")
        events = list(events.values())
    while isinstance(events, GeneratorType) or inspect.isgeneratorfunction(events):
        log.debug(f"Casting matching events, detected {type(events)}({events})")
        log.debug("swapping stdout and stderr")
        orig_stderr = sys.stderr
        orig_stdout = sys.stdout
        sys.stderr = StringIO()
        sys.stdout = StringIO()
        try:
            log.debug(f"Attempting to cast events to list")
            events = list(events)
            log.debug(f"Successfully cast events as list, {len(events)} events found")
        except (Exception, SystemExit) as exception:
            log.exception("An unhandled exception occurred")
            try:
                sys.stderr.seek(0)
                sys.stdout.seek(0)
            except:
                log.exception("An Unhandled exception occurred.")
            return [
                {
                    "stdout": sys.stdout.read(),
                    "stderr": sys.stderr.read(),
                    "exception": str(exception),
                    "matching_events": events,
                },
            ]
        finally:
            log.debug("replacing original stdout and stderr")
            sys.stderr = orig_stderr
            sys.stdout = orig_stdout

    if isinstance(events, list):
        log.debug(f"Found matching_events: {events}")
        # Peek at the data type of the first item
        if events and isinstance(events[0], BaseEvent):
            log.debug(f"Found list of Events, converting to dicts")
            events = [custom_model_to_dict(event) for event in events]
            log.debug(f"Successfully converted to dicts")
        if events and isinstance(events[0], dict):
            # keys is a set of all keys from all events in matching_events
            log.debug(f"Found list of dicts, attempting to ensure all keys are present in each event.")
            keys = set(chain.from_iterable(events))
            log.debug(f"Found keys: {keys}")
            for item in events:
                # Add None to fill any missing values
                # log.debug(f"Found item: {item}")
                if isinstance(item, dict):
                    localize_datetimes(item)
                    # log.debug(f"Adding missing keys")
                    try:
                        item.update({key: item.get(key, None) for key in keys})
                    except:
                        log.debug(f"Found item: {type(item)}({item})")
                        raise
    return events
