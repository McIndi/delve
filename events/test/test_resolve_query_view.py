# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""This test module is meant to test events.api.ResolveQueryView.

These tests will rely on a couple of search_commands to be configured to pass,
but that will be kept to a minimum.
"""

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import (
    APITestCase,
    APIRequestFactory,
    APIClient,
    force_authenticate,
)

from events.models import (
    Event,
    Query,
)

class ResolveQueryViewTests(APITestCase):
    def setUp(self, *args, **kwargs):
        """For preparation, we are going to setup a user and
        an APIClient.
        """
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testuser',
            
        )
        self.user.save()

        self.admin_user = get_user_model().objects.create_user(
            username='testadmin',
            email='testadmin@test.com',
            password='testadmin',
            
        )
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        super().setUp(*args, **kwargs)

    def test_create_one_event_and_retrieve_it_with_query(self):
        event_list_url = reverse('event-list')
        query_list_url = reverse('api_query')
        query_data = {
            'name': 'test-001', 
            'text': 'search',
        }
        event_data = {
            'index': 'default',
            'host': '127.0.0.1',
            'source': 'system',
            'sourcetype': 'json',
            'text': '{"foo": "bar"}',
        }
        self.client.login(username='testadmin', password='testadmin')
        event_response = self.client.post(
            event_list_url,
            data=event_data,
        )
        query_response = self.client.post(
            query_list_url,
            data=query_data,
        )
        self.client.logout()
        self.assertEqual(query_response.status_code, status.HTTP_200_OK)
        self.assertEqual(event_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(query_response.json()), 1)
        self.assertEqual(query_response.json()[0]['index'], 'default')
        # Make sure that the fields were extracted
        self.assertEqual(query_response.json()[0]['extracted_fields']['foo'], 'bar') 
        self.assertIsInstance(query_response.json(), list)

        # This view does not save the queries by default
        self.assertEqual(Query.objects.count(), 0)

    # def test_cannot_retrieve_other_users_events_through_query(self):
    #     query_url = reverse('api_query')
    #     query_data = {
    #         'name': 'test-001',
    #         'text': 'search',
    #     }
    #     event_list_url = reverse('event-list')
    #     event_data = {
    #         'index': 'default',
    #         'host': '127.0.0.1',
    #         'source': 'system',
    #         'sourcetype': 'json',
    #         'text': '{"foo": "bar"}',
    #     }

    #     # First, create a an event as admin
    #     self.client.login(username='testadmin', password='testadmin')
    #     response = self.client.post(
    #         event_list_url,
    #         data=event_data,
    #     )
    #     self.client.logout()
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Event.objects.count(), 1)

    #     # Second, login as user and resolve a query for all events, should return empty
    #     self.client.login(username='testuser', password='testuser')
    #     response = self.client.post(
    #         query_url,
    #         data=query_data,
    #     )
    #     response_json = response.json()
    #     self.client.logout()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response_json), 0)

    #     # Third, login as admin and resolve a query for all events, should return
    #     # the previously created event
    #     self.client.login(username='testadmin', password='testadmin')
    #     response = self.client.post(
    #         query_url,
    #         data=query_data,
    #     )
    #     response_json = response.json()
    #     self.client.logout()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response_json), 1)
