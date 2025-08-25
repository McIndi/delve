# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from functools import wraps
from typing import Optional, List, Callable, Any

import pydantic

def search_command(parser: argparse.ArgumentParser, input_validators: Optional[List[pydantic.BaseModel]] = None) -> Callable:
    """
    Decorator to register a search command.

    This decorator attaches an ArgumentParser instance and optional Pydantic input validators to the decorated function.
    The ArgumentParser is used to create help text in the web UI.

    Args:
        parser (argparse.ArgumentParser): The argument parser for the command.
        input_validators (Optional[List[pydantic.BaseModel]]): List of input validators.

    Returns:
        Callable: The decorated function.
    """
    def _decorator(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            log = logging.getLogger(__name__)
            log.info(f"Executing search command: {func.__name__}")
            result = func(*args, **kwargs)
            return result
        inner.parser = parser
        inner.input_validators = input_validators
        return inner
    return _decorator

