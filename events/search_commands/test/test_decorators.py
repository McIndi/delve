# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""This test module is meant to test the decorators module,
located at events.search_commands.decorators.
"""
import unittest
import argparse
from unittest.mock import MagicMock
from typing import Any, Dict, List

from django.http import HttpRequest

from events.search_commands.decorators import search_command

class DecoratorsTests(unittest.TestCase):
    def test_search_command_decorator(self) -> None:
        """Test the search_command decorator to ensure it correctly registers
        a search command and attaches the ArgumentParser.
        """
        mock_parser = argparse.ArgumentParser(
            prog="mock_command",
            description="Mock command for testing",
        )

        @search_command(mock_parser)
        def mock_command(request: HttpRequest, events: List[Dict[str, Any]], argv: List[str], environment: Dict[str, Any]) -> str:
            return "success"

        # Check if the parser is attached to the decorated function
        self.assertEqual(mock_command.parser, mock_parser)

        # Execute the decorated function and check the result
        result = mock_command(None, [], [], {})
        self.assertEqual(result, "success")

if __name__ == "__main__":
    unittest.main()
