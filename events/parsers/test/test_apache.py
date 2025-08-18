# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import unittest
from src.home.events.parsers.apache import apache

class TestApacheParser(unittest.TestCase):
    def test_apache_parser_valid_line(self):
        sample_line = '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'
        result = apache(sample_line)
        self.assertEqual(result["host"], "127.0.0.1")
        self.assertEqual(result["time"], "[10/Oct/2000:13:55:36 -0700]")
        self.assertEqual(result["request"], "GET /apache_pb.gif HTTP/1.0")
        self.assertEqual(result["status"], "200")
        self.assertEqual(result["size"], "2326")

if __name__ == '__main__':
    unittest.main()