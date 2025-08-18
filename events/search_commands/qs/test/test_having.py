# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""This test module is meant to test the having search
command, located at events.search_commands.qs.having.
"""
import json
from unittest.mock import MagicMock

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

class HavingTests(APITestCase):
    def setUp(self, *args, **kwargs):
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
                        "foo": i % 3,
                        "bar": i % 2,
                    }
                )
            )
            event.extract_fields()
            event.process()
            event.save()
            self.events.append(event)
        super().setUp(*args, **kwargs)

    def test_having(self):
        """Test the having command to ensure it correctly filters
        the grouped records from the QuerySet based on the provided expressions.
        """
        query = Query(
            name="test",
            text="search index=test | qs_group_by extracted_fields__foo bar=Cast(KT(extracted_fields__bar),IntegerField) | qs_having extracted_fields__foo__gt=1",
            user=self.user,
        )
        results = query.resolve(
            request=MagicMock(user=self.user),
        )
        # Expected Results: [{'extracted_fields__foo': 2, 'bar': 0}, {'extracted_fields__foo': 2, 'bar': 1}, {'extracted_fields__foo': 2, 'bar': 0}]
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['bar'], 0)
        self.assertEqual(results[1]['bar'], 1)
        self.assertEqual(results[2]['bar'], 0)
