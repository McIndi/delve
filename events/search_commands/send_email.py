# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from django.core.mail import send_mail
from typing import Any, Dict, List, Union
from django.http import HttpRequest
import argparse
import logging

from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="send_email",
    description="Send an email notification based on the result set",
)
parser.add_argument(
    "recipient",
    type=str,
    help="The recipient email address",
)
parser.add_argument(
    "subject",
    type=str,
    help="The email subject",
)
parser.add_argument(
    "message",
    type=str,
    nargs="+",
    help="The email message",
)

@search_command(parser)
def send_email(request: HttpRequest, events: Union[List[Dict[str, Any]], Any], argv: List[str], context: Dict[str, Any]) -> Union[List[Dict[str, Any]], Any]:
    """
    Send an email notification based on the result set.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[List[Dict[str, Any]], Any]): The list of events.
        argv (List[str]): The list of command arguments.
        context (Dict[str, Any]): The context dictionary.

    Returns:
        Union[List[Dict[str, Any]], Any]: The list of events.
    """
    log = logging.getLogger(__name__)
    log.debug(f"Found events: {events}")
    args = send_email.parser.parse_args(argv[1:])
    log.debug(f"Found args: {args}")

    if not events:
        return events


    send_mail(
        subject=args.subject,
        message=' '.join(args.message),
        from_email='no-reply@yourdomain.com',
        recipient_list=[args.recipient],
    )

    return events
