# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""This test module is meant to test events.api.QueryViewSet.

Not a lot to test here, because this viewset does not allow resolving the query.
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

class QueryViewsetTests(APITestCase):
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

    def test_create_query(self):
        url = reverse('query-list')
        data = {
            'name': 'test-001', 
            'text': 'search',
        }
        self.client.login(username='testadmin', password='testadmin')
        response = self.client.post(
            url,
            data=data,
        )
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Query.objects.count(), 1)
        self.assertEqual(Query.objects.get().name, 'test-001')

    def test_cannot_retrieve_other_users_queries(self):
        # First, create a query as admin
        url = reverse('query-list')
        data = {
            'name': 'test-001', 
            'text': 'search',
        }
        self.client.login(username='testadmin', password='testadmin')
        response = self.client.post(
            url,
            data=data,
        )
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Query.objects.count(), 1)
        self.assertEqual(Query.objects.get().name, 'test-001')
        admins_query_pk = Query.objects.get().pk

        # Second, login as user and get list of queries, the one previously created should not be found
        self.client.login(username='testuser', password='testuser')
        response = self.client.get(url)
        response_json = response.json()
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json['results']), 0)

        # Third, login as user and try to get the previously created query using pk
        # should fail
        self.client.login(username='testuser', password='testuser')
        url = reverse('query-detail', args=[admins_query_pk])
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(response_json['results']), 0)

        # Login as admin and make sure we can successfully retrieve the previously created query 
        self.client.login(username='testadmin', password='testadmin')
        url = reverse('query-detail', args=[admins_query_pk])
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json['results']), 0)
