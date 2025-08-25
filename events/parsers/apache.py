# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""Module for parsing Apache HTTP server access logs."""

import re
from typing import Dict

HOST = r'^(?P<host>.*?)'
SPACE = r'\s'
IDENTITY = r'\S+'
USER = r'\S+'
TIME = r'(?P<time>\[.*?\])'
REQUEST = r'\"(?P<request>.*?)\"'
STATUS = r'(?P<status>\d{3})'
SIZE = r'(?P<size>\S+)'
REGEX = HOST + SPACE + IDENTITY + SPACE + USER + SPACE + TIME + SPACE + REQUEST + SPACE + STATUS + SPACE + SIZE + SPACE

def apache(log_line: str) -> Dict[str, str]:
    """Parse a single Apache log line and return relevant attributes."""
    # Use regex to extract fields from the provided log line
    match = re.search(REGEX, log_line)
    return {
        "host": match.group('host'),
        "time": match.group('time'), 
        "request": match.group('request'),
        "status": match.group('status'),
        "size": match.group('size'),
    }
