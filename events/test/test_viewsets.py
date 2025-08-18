# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from io import StringIO
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status

from rest_framework.test import (
    APITestCase,
    APIRequestFactory,
    APIClient,
    force_authenticate,
)
from events.models import Event

class EventViewSetTests(APITestCase):

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
        super().setUp(*args, **kwargs)

    def test_event_list_get(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('event-list')
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_create_post(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('event-list')
        response = self.client.post(url, data={
            "text": "test",
        })
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_retrieve_get(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('event-list')
        response = self.client.post(url, data={
            "text": "test",
        })
        _id = Event.objects.get().id
        url = reverse('event-detail', kwargs={'pk': _id})
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_update_put(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('event-list')
        response = self.client.post(url, data={
            "text": "test",
        })
        _id = Event.objects.get().id
        url = reverse('event-detail', kwargs={'pk': _id})
        response = self.client.put(url, data={
            "text": "test-02"
        })
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_partial_update_patch(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('event-list')
        response = self.client.post(url, data={
            "text": "test",
        })
        _id = Event.objects.get().id
        url = reverse('event-detail', kwargs={'pk': _id})
        response = self.client.patch(url, data={})
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_destroy_delete(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('event-list')
        response = self.client.post(url, data={
            "text": "test",
        })
        _id = Event.objects.get().id
        url = reverse('event-detail', kwargs={'pk': _id})
        response = self.client.delete(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SearchCommandViewSetTests(APITestCase):

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
        super().setUp(*args, **kwargs)

    def test_SearchCommands_list_get(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('SearchCommands-list')
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class QueryViewTests(APITestCase):

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
        super().setUp(*args, **kwargs)

    def test_query_list_get(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('query-list')
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_query_create_post(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('query-list')
        response = self.client.post(url, data={
            "name": "",
            "text": "search",
        })
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_query_retrieve_get(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('query-list')
        response = self.client.post(url, data={
            "name": "",
            "text": "search",
        })
        _id = response.json()["id"]
        url = reverse('query-detail', kwargs={'pk': _id})
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_query_update_put(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('query-list')
        response = self.client.post(url, data={
            "name": "",
            "text": "search",
        })
        _id = response.json()["id"]
        url = reverse('query-detail', kwargs={'pk': _id})
        response = self.client.put(url, data={
            "name": "",
            "text": "search",
        })
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_query_partial_update_patch(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('query-list')
        response = self.client.post(url, data={
            "name": "",
            "text": "search",
        })
        _id = response.json()["id"]
        url = reverse('query-detail', kwargs={'pk': _id})
        response = self.client.patch(url, data={})
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_query_destroy_delete(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('query-list')
        response = self.client.post(url, data={
            "name": "",
            "text": "search",
        })
        _id = response.json()["id"]
        url = reverse('query-detail', kwargs={'pk': _id})
        response = self.client.delete(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class GlobalContextViewSetTests(APITestCase):

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
        super().setUp(*args, **kwargs)

    def test_globalcontext_list_get(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('globalcontext-list')
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_globalcontext_create_post(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('globalcontext-list')
        response = self.client.post(url, data={})
        self.client.logout()
        # Expect 200 because GlobalContextis unique per user, so update on POST
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_globalcontext_retrieve_get(self):
        self.client.login(username='testuser', password='testuser')
        _id = self.user.global_context.id
        url = reverse('globalcontext-detail', kwargs={'pk': _id})
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_globalcontext_update_put(self):
        self.client.login(username='testuser', password='testuser')
        _id = self.user.global_context.id
        url = reverse('globalcontext-detail', kwargs={'pk': _id})
        response = self.client.put(url, data={})
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_globalcontext_partial_update_patch(self):
        self.client.login(username='testuser', password='testuser')
        _id = self.user.global_context.id
        url = reverse('globalcontext-detail', kwargs={'pk': _id})
        response = self.client.patch(url, data={})
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_globalcontext_destroy_delete(self):
        self.client.login(username='testuser', password='testuser')
        _id = self.user.global_context.id
        url = reverse('globalcontext-detail', kwargs={'pk': _id})
        response = self.client.delete(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class LocalContextViewSetTests(APITestCase):

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
        super().setUp(*args, **kwargs)

    def test_localcontext_list_get(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('localcontext-list')
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_localcontext_create_post(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('localcontext-list')
        response = self.client.post(
            url,
            format="json",
            data={
            "name": "test",
            "context": {
                "test": "test",
            }
        })
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_localcontext_retrieve_get(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('localcontext-list')
        response = self.client.post(
            url,
            format="json",
            data={
            "name": "test",
            "context": {
                "test": "test",
            }
        })
        _id = response.json()["id"]
        url = reverse('localcontext-detail', kwargs={'pk': _id})
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_localcontext_update_put(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('localcontext-list')
        response = self.client.post(
            url,
            format="json",
            data={
            "name": "test",
            "context": {
                "test": "test",
            }
        })
        _id = response.json()["id"]
        url = reverse('localcontext-detail', kwargs={'pk': _id})
        response = self.client.put(
            url,
            format="json",
            data={
            "name": "test-02",
            "context": {
                "test-02": "test-02",
            }
        })
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_localcontext_partial_update_patch(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('localcontext-list')
        response = self.client.post(
            url,
            format="json",
            data={
            "name": "test",
            "context": {
                "test": "test",
            }
        })
        _id = response.json()["id"]
        url = reverse('localcontext-detail', kwargs={'pk': _id})
        response = self.client.patch(url, data={})
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_localcontext_destroy_delete(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('localcontext-list')
        response = self.client.post(
            url,
            format="json",
            data={
            "name": "test",
            "context": {
                "test": "test",
            }
        })
        _id = response.json()["id"]
        url = reverse('localcontext-detail', kwargs={'pk': _id})
        response = self.client.delete(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class FileUploadViewSetTests(APITestCase):

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
        super().setUp(*args, **kwargs)

    def test_fileupload_list_get(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('fileupload-list')
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fileupload_create_post(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('fileupload-list')
        response = self.client.post(url, data={
            "title": "test",
            "content": StringIO("test"),
        })
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fileupload_retrieve_get(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('fileupload-list')
        response = self.client.post(url, data={
            "title": "test",
            "content": StringIO("test"),
        })
        _id = response.json()["id"]
        url = reverse('fileupload-detail', kwargs={'pk': _id})
        response = self.client.get(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fileupload_update_put(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('fileupload-list')
        response = self.client.post(url, data={
            "title": "test",
            "content": StringIO("test"),
        })
        _id = response.json()["id"]
        url = reverse('fileupload-detail', kwargs={'pk': _id})
        response = self.client.put(url, data={
            "title": "test-02",
            "content": StringIO("test-02")
        })
        self.client.logout()
        self.assertEqual(response.json()["title"], "test-02")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fileupload_partial_update_patch(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('fileupload-list')
        response = self.client.post(url, data={
            "title": "test",
            "content": StringIO("test"),
        })
        _id = response.json()["id"]
        url = reverse('fileupload-detail', kwargs={'pk': _id})
        response = self.client.patch(url, data={})
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fileupload_destroy_delete(self):
        self.client.login(username='testuser', password='testuser')
        url = reverse('fileupload-list')
        response = self.client.post(url, data={
            "title": "test",
            "content": StringIO("test"),
        })
        _id = response.json()["id"]
        url = reverse('fileupload-detail', kwargs={'pk': _id})
        response = self.client.delete(url)
        self.client.logout()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
