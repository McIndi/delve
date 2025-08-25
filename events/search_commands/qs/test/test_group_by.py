# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""This test module is meant to test the group_by search
command, located at events.search_commands.qs.group_by.
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

class GroupByTests(APITestCase):
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
                host=f"127.0.0.{i%3}",
                source="test",
                sourcetype="json",
                user=self.user,
                text=json.dumps(
                    {
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

    def test_group_by(self):
        """Test the group_by command to ensure it correctly groups
        the records from the QuerySet based on the provided expressions.
        """
        query = Query(
            name="test",
            text="search index=test | qs_group_by host avg_bar=Avg(Cast(extracted_fields__bar,IntegerField))",
            user=self.user,
        )
        results = query.resolve(
            request=MagicMock(user=self.user),
        )
        # Expected result: [{'host': '127.0.0.0', 'avg_bar': 0.5}, {'host': '127.0.0.1', 'avg_bar': 0.6666666666666666}, {'host': '127.0.0.2', 'avg_bar': 0.3333333333333333}]
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['avg_bar'], 0.5)
        self.assertAlmostEqual(results[1]['avg_bar'], 0.6666666666666666, places=4)
        self.assertAlmostEqual(results[2]['avg_bar'], 0.3333333333333333, places=4)
        self.assertEqual(results[0]['host'], '127.0.0.0')
        self.assertEqual(results[1]['host'], '127.0.0.1')
        self.assertEqual(results[2]['host'], '127.0.0.2')