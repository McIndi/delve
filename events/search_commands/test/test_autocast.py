# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""This test module is meant to test the autocast search
command, located at events.search_commands.autocast.
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

class AutoCastTests(APITestCase):
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
                        "int": str(i),
                        "float": str(float(i)),
                        "boolean": "True",
                        "list": "[1,2,3]",
                        "dict": "{'key': 'value'}",
                    }
                )
            )
            event.extract_fields()
            event.process()
            event.save()
            self.events.append(event)
        super().setUp(*args, **kwargs)

    def test_autocast_everything_else_worked(self) -> None:
        """Basic sanity checks, if this does not work, it is not autocast,
        but rather something with event.models.Query or event.models.Query.resolve
        or we were unable to create test events
        """
        query = Query(
            name="test",
            text="search index=test",
            user=self.user,
        )
        results = query.resolve(request=MagicMock(user=self.user))
        self.assertEqual(len(results), 10)

    def test_autocast_casts_ints(self) -> None:
        """Test that autocast correctly casts integer fields."""
        query = Query(
            name="test",
            text="search index=test | explode extracted_fields | autocast int",
            user=self.user,
        )
        results = query.resolve(
            request=MagicMock(user=self.user),
        )
        self.assertEqual(len(results), 10)
        self.assertIsInstance(results[0]["int"], int)

    def test_autocast_casts_float(self) -> None:
        """Test that autocast correctly casts float fields."""
        query = Query(
            name="test",
            text="search index=test | explode extracted_fields | autocast float",
            user=self.user,
        )
        results = query.resolve(
            request=MagicMock(user=self.user),
        )
        self.assertEqual(len(results), 10)
        self.assertIsInstance(results[0]["float"], float)

    def test_autocast_casts_boolean(self) -> None:
        """Test that autocast correctly casts boolean fields."""
        query = Query(
            name="test",
            text="search index=test | explode extracted_fields | autocast boolean",
            user=self.user,
        )
        results = query.resolve(
            request=MagicMock(user=self.user),
        )
        self.assertEqual(len(results), 10)
        self.assertIsInstance(results[0]["boolean"], bool)

    def test_autocast_casts_list(self) -> None:
        """Test that autocast correctly casts list fields."""
        query = Query(
            name="test",
            text="search index=test | explode extracted_fields | autocast list",
            user=self.user,
        )
        results = query.resolve(
            request=MagicMock(user=self.user),
        )
        self.assertEqual(len(results), 10)
        self.assertIsInstance(results[0]["list"], list)

    def test_autocast_casts_dict(self) -> None:
        """Test that autocast correctly casts dictionary fields."""
        query = Query(
            name="test",
            text="search index=test | explode extracted_fields | autocast dict",
            user=self.user,
        )
        results = query.resolve(
            request=MagicMock(user=self.user),
        )
        self.assertEqual(len(results), 10)
        self.assertIsInstance(results[0]["dict"], dict)

