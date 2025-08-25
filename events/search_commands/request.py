# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""Issue an HTTP request to retrieve data."""
from urllib.parse import urlparse
import datetime
import argparse
import logging
import json
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils import timezone

import requests

from events.models import Event
from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="request",
    description="Make an HTTP request."
)
parser.add_argument(
    "method",
    default="GET",
    choices=(
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
        "HEAD",
    ),
    help="The method for the request. (default GET)"
)
parser.add_argument(
    "url",
    help="The URL to send the HTTP request to",
)
parser.add_argument(
    "--username",
    help="The username to use for auth",
)
parser.add_argument(
    "--password",
    help="The password to use for auth"
)
parser.add_argument(
    "--kv-pairs",
    action="append",
    help="Add key-value pair to the querystring for GET requests and application/x-www-form-urlencoded for POST, PATCH, and PUT requests. Unless --json is passed, in which case application/json will be used",
)
parser.add_argument(
    "--json",
    action="store_true",
    help="If sending POST, PUT, or PATCH requests, encode any key-value pair in the request body as JSON",
)
parser.add_argument(
    "--save-event",
    action="store_true",
    help="If specified, an event will be saved with the result of the request.",
)
parser.add_argument(
    "--extract-fields",
    action="store_true",
    help="If specified, fields will be extracted from events regardless of whether the event was saved",
)
parser.add_argument(
    "--recent-ok",
    action="store_true",
    help="If specified, the latest event from the same user, host, URI, and method will be returned as long as it is not older than the number of minutes specified by --recent-minutes",
)
parser.add_argument(
    "--recent-minutes",
    type=int,
    default=5,
    help="The max age, in minutes, for an event to be considered recent",
)
parser.add_argument(
    "-H",
    "--headers",
    action="append",
    help="Provide HTTP headers for the request, can be specified multiple times",
)
parser.add_argument(
    "-n",
    "--no-verify",
    action="store_true",
    help="If specified, SSL certificates will not be verified",
)

@search_command(parser)
def make_request(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Issue an HTTP request to retrieve data.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the result of the HTTP request.
    """
    log = logging.getLogger(__name__)

    log.debug(f"Received {len(argv)} items in argv")
    if "request" in argv:
        argv.pop(argv.index("request"))
    args = make_request.parser.parse_args(argv)
    log.debug(f"Parsed args: {args}")
    headers = args.headers
    log.debug(f"Found headers: {headers}")
    if headers:
        headers = {i.split('=', 1)[0]: i.split('=', 1)[1] for i in args.headers}
    else:
        headers = {}
    log.debug(f"Parsed headers: {headers}")
    body = {}
    if args.kv_pairs:
        log.debug(f"Found kv_pairs: {args.kv_pairs}")
        for kv_pair in args.kv_pairs:
            log.debug(f"Found kv_pair: {kv_pair}")
            key, value = kv_pair.split("=", 1)
            log.debug(f"Found key, value: {key}, {value}")
            body[key] = value

    kwargs = {
        "method": args.method,
        "url": args.url,
        "headers": headers,
        "verify": not args.no_verify,
    }
    log.debug(f"Built request kwargs: {kwargs}")
    if args.username and args.password:
        log.debug(f"Adding auth for {args.username}")
        kwargs.update(
            {
                "auth": (args.username, args.password),
            }
        )
    if body:
        if args.method == "GET":
            log.debug("Updating params")
            kwargs.update(
                {
                    "params": body
                }
            )
        elif args.method in ["POST", "PUT", "PATCH"]:
            if args.json:
                log.debug("Updating json body")
                kwargs.update(
                    {
                        "json": body,
                    }
                )
            else:
                log.debug("Updating body")
                kwargs.update(
                    {
                        "data": body,
                    }
                )

    parsed_url = urlparse(kwargs["url"])
    if args.recent_ok:
        events = Event.objects.filter(
            index="http.request",
            host=parsed_url.netloc,
            source=parsed_url.path,
            user=request.user,
            created__gt=timezone.now() - datetime.timedelta(minutes=args.recent_minutes)
        )
        if events.exists():
            event = events.order_by("-created").first()
            return [event]

    log.debug("Sending request")
    response = requests.request(**kwargs)
    log.debug(f"Received response: {response}")
    response_json = None
    event = None
    try:
        log.debug(f"Attempting to parse response as json")
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        log.debug("Json parsing failed, using text")
        event = Event(
            index="http.request",
            host=parsed_url.netloc,
            source=parsed_url.path,
            sourcetype="text",
            text=response.text,
            user=request.user,
        )
        if args.save_event:
            event.save()
        elif args.extract_fields:
            event.extract_fields()
        return [event]

    if response_json is None:
        log.debug(f"Found response_json to be empty")
        event = Event(
            index="http.request",
            host=parsed_url.netloc,
            source=parsed_url.path,
            sourcetype="text",
            text=response.text,
            user=request.user,
            extracted_fields={"status_code": response.status_code}
        )
        if args.save_event:
            event.save()
        elif args.extract_fields:
            event.extract_fields()
        return [event]
    else:
        log.debug(f"response_json found to be list, dict, scalar or other. Will yield as one unit")
        event = Event(
            index="http.request",
            host=parsed_url.netloc,
            source=parsed_url.path,
            sourcetype="json",
            text=json.dumps(response_json),
            user=request.user,
            extracted_fields={"status_code": response.status_code},
        )
        if args.save_event:
            event.save()
        elif args.extract_fields:
            event.extract_fields()
        return [event]

