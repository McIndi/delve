# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""This test module is meant to test the explode_timestamp command,
located at events.search_commands.explode_timestamp.
"""
import json
from unittest.mock import MagicMock
from typing import Any

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import (
    APITestCase,
    APIRequestFactory,
    APIClient,
)

from events.models import (
    Event,
    Query,
)

TEST_USER = "testuser"
TEST_USER_PASS = "testuser"
TEST_ADMIN = "testadmin"
TEST_ADMIN_PASS = "testadmin"

class ExplodeTimestampTests(APITestCase):
    def setUp(self, *args: Any, **kwargs: Any) -> None:
        """For preparation, we are going to setup a user and
        an APIClient and add ten Events.
        """
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testuser',
        )
        self.user.save()
        self.events = []
        for i in range(10):
            event = Event.objects.create(
                index="test",
                host="127.0.0.1",
                source="test",
                sourcetype="json",
                user=self.user,
                text=json.dumps(
                    {
                        "timestamp": f"2023-01-01T00:00:0{i}",
                        "foo": i,
                        "bar": i % 2,
                    }
                )
            )
            event.extract_fields()
            event.process()
            event.save()
            self.events.append(event)
        super().setUp(*args, **kwargs)

    def test_explode_timestamp(self) -> None:
        """Test the explode_timestamp command to ensure it correctly explodes
        the timestamp field into separate date and time fields.
        """
        query = Query(
            name="test",
            text="search index=test | explode extracted_fields | mark_timestamp timestamp |  explode_timestamp timestamp",
            user=self.user,
        )
        results = query.resolve(
            request=MagicMock(user=self.user),
        )
        self.assertEqual(len(results), 10)
        self.assertIn('year', results[0])
        self.assertIn('month', results[0])
        self.assertIn('day', results[0])
        self.assertIn('hour', results[0])
        self.assertIn('minute', results[0])
        self.assertIn('second', results[0])
        self.assertIn('microsecond', results[0])
        self.assertEqual(results[0]['year'], 2023)
        self.assertEqual(results[0]['month'], 1)
        self.assertEqual(results[0]['day'], 1)
        self.assertEqual(results[0]['hour'], 0)
        self.assertEqual(results[0]['minute'], 0)
        self.assertEqual(results[0]['second'], 0)
        self.assertEqual(results[0]['microsecond'], 0)
