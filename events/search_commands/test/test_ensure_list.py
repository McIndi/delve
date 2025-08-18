# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""This test module is meant to test the ensure_list search
command, located at events.search_commands.ensure_list.
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

class EnsureListTests(APITestCase):
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
                        "foo": i,
                    }
                )
            )
            event.extract_fields()
            event.process()
            event.save()
            self.events.append(event)
        super().setUp(*args, **kwargs)

    def test_ensure_list_everything_else_worked(self) -> None:
        """Basic sanity checks, if this does not work, it is not ensure_list,
        but rather something with event.models.Query or event.models.Query.resolve
        or we were unable to create test events.
        """
        query = Query(
            name="test",
            text="search index=test",
            user=self.user,
        )
        results = query.resolve(request=MagicMock(user=self.user))
        self.assertEqual(len(results), 10)

    def test_ensure_list_casts_field_as_list(self) -> None:
        """Test that ensure_list correctly casts the specified field as a list."""
        query = Query(
            name="test",
            text="search index=test",
            user=self.user,
        )
        results = query.resolve(
            request=MagicMock(user=self.user),
        )
        self.assertIsInstance(results[0]["index"], str)
        
        query = Query(
            name="test",
            text="search index=test | ensure_list index",
            user=self.user,
        )
        results = query.resolve(
            request=MagicMock(user=self.user),
        )
        self.assertIsInstance(results[0]["index"], list)

