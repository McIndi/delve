# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""This test module is meant to test events.api.EventViewSet.
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
)


# from apps.core import models, admin
# from apps.rest import views

class EventViewsetTests(APITestCase):
    def setUp(self, *args, **kwargs):
        """For preparation, we are going to setup a user and
        an APIClient.
        """
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testadmin',
            email='testadmin@test.com',
            password='testadmin',
            
        )
        # self.user.is_superuser = True
        # self.user.is_staff = True
        self.user.save()
        super().setUp(*args, **kwargs)

    def test_create_event_unauthenticated_fails(self):
        """Ensure we receive a HTTP 401 UNAUTHORIZED when attampting to create
        an event without authenticating.
        """
        
        url = reverse('event-list')
        data = {
            'index': 'test',
            'host': '127.0.0.1',
            'source': 'system',
            'sourcetype': 'json',
            'text': '{"foo": "bar"}',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Event.objects.count(), 0)

    def test_create_event_authenticated_succedes(self):
        """Ensure we receive a HTTP 201 CREATED when attampting to create
        an event with proper authentication.
        """
        url = reverse('event-list')
        data = {
            'index': 'test',
            'host': '127.0.0.1',
            'source': 'system',
            'sourcetype': 'json',
            'text': '{"foo": "bar"}',
        }
        self.client.login(username='testadmin', password='testadmin')
        response = self.client.post(url, data)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().index, 'test')

    def test_create_multiple_events(self):
        """Ensure we receive a HTTP 201 CREATED when attampting to create
        multiple events while properly authenticated.
        """
        url = reverse('event-list')
        self.client.login(username='testadmin', password='testadmin')
        data = []
        for i in range(10):
            data.append(
                {
                    'index': 'test',
                    'host': '127.0.0.1',
                    'source': 'system',
                    'sourcetype': 'json',
                    'text': f'{{"reading": {2*i}}}',
                }
            )
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 10)
        self.client.logout()

    def test_json_field_extractions_while_enabled(self):
        """Ensure that when enabled, JSON fields will be extracted 
        when creating an event.
        """
        url = reverse('event-list')
        data = {
            'index': 'test',
            'host': '127.0.0.1',
            'source': 'system',
            'sourcetype': 'json',
            'text': '{"foo": "bar"}',
        }
        with self.settings(DELVE_ENABLE_EXTRACTIONS_ON_CREATE=True):
            self.client.login(username='testadmin', password='testadmin')
            response = self.client.post(url, data)
            # response_json = response.json()
            self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().index, 'test')
        self.assertEqual(Event.objects.get().extracted_fields['foo'], 'bar')
        # self.assertEqual(response_json['extracted_fields']['foo'], 'bar')

    def test_json_field_extractions_while_disabled(self):
        """Ensure that when disabled, JSON fields will not be extracted 
        when creating an event.
        """
        url = reverse('event-list')
        data = {
            'index': 'test',
            'host': '127.0.0.1',
            'source': 'system',
            'sourcetype': 'json',
            'text': '{"foo": "bar"}',
        }
        with self.settings(DELVE_ENABLE_EXTRACTIONS_ON_CREATE=False):
            self.client.login(username='testadmin', password='testadmin')
            response = self.client.post(url, data)
            # response_json = response.json()
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().index, 'test')
        self.assertEqual(Event.objects.get().extracted_fields, {})

    def test_patch_update_event_with_update_extractions_enabled(self):
        """Ensure that when enabled, JSON fields will be extracted again
        when updating an event.
        """
        url = reverse('event-list')
        data = {
            'index': 'test',
            'host': '127.0.0.1',
            'source': 'system',
            'sourcetype': 'json',
            'text': '{"foo": "bar"}',
        }
        self.client.login(username='testadmin', password='testadmin')
        response = self.client.post(url, data)
        # response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().index, 'test')
        self.assertEqual(Event.objects.get().extracted_fields['foo'], 'bar')
        # self.assertEqual(response_json['extracted_fields']['foo'], 'bar')

        with self.settings(DELVE_ENABLE_EXTRACTIONS_ON_UPDATE=True):
            # With this setting as True, fields should be re-extracted during an update
            response = self.client.patch(
                reverse('event-detail', args=[Event.objects.get().id]),
                {
                    'text': '{"foo": "baz"}',
                },
            )
            response_json = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Event.objects.count(), 1)
            self.assertEqual(Event.objects.get().index, 'test')
            self.assertEqual(Event.objects.get().text, '{"foo": "baz"}')
            self.assertEqual(Event.objects.get().extracted_fields['foo'], 'baz')
            self.assertEqual(response_json['extracted_fields']['foo'], 'baz')
        self.client.logout()

    def test_patch_update_event_with_update_extractions_disabled(self):
        """Ensure that when disabled, JSON fields will not be extracted again
        when updating an event.
        """
        url = reverse('event-list')
        data = {
            'index': 'test',
            'host': '127.0.0.1',
            'source': 'system',
            'sourcetype': 'json',
            'text': '{"foo": "bar"}',
        }
        self.client.login(username='testadmin', password='testadmin')
        response = self.client.post(url, data)
        # response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().index, 'test')
        self.assertEqual(Event.objects.get().extracted_fields['foo'], 'bar')
        # self.assertEqual(response_json['extracted_fields']['foo'], 'bar')

        with self.settings(DELVE_ENABLE_EXTRACTIONS_ON_UPDATE=False):
            # With this setting as False, fields should NOT be re-extracted during an update
            response = self.client.patch(
                reverse('event-detail', args=[Event.objects.get().id]),
                {
                    'text': '{"foo": "baz"}',
                },
            )
            # response_json = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Event.objects.count(), 1)
            self.assertEqual(Event.objects.get().index, 'test')
            self.assertEqual(Event.objects.get().text, '{"foo": "baz"}')
            self.assertEqual(Event.objects.get().extracted_fields['foo'], 'bar')
            # self.assertEqual(response_json['extracted_fields']['foo'], 'bar')
        self.client.logout()

