# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""This test module is meant to test the annotate search
command, located at events.search_commands.qs.annotate.
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

class AnnotateTests(APITestCase):
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

    def test_simple_annotation(self):
        """Test the annotate command to ensure it correctly annotates
        the events with the specified fields.
        """
        query = Query(
            name="test",
            text="search index=test | qs_annotate foo=Cast(KT(extracted_fields__foo),IntegerField) bar=Cast(KT(extracted_fields__bar),IntegerField)",
            user=self.user,
        )
        results = query.resolve(
            request=MagicMock(user=self.user),
        )
        self.assertEqual(results[0]['foo'], 0)
        self.assertEqual(results[1]['foo'], 1)
        self.assertEqual(results[2]['foo'], 2)
        self.assertEqual(results[0]['bar'], 0)
        self.assertEqual(results[1]['bar'], 1)
        self.assertEqual(results[2]['bar'], 0)
