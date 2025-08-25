# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from django.core import mail
from django.test import TestCase, RequestFactory
from unittest.mock import MagicMock
from events.models import Event, Query
from events.search_commands.send_email import send_email
from django.contrib.auth import get_user_model

class SendEmailCommandTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
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
                sourcetype="text",
                user=self.user,
                text=f"Test event {i}",
            )
            event.extract_fields()
            event.process()
            event.save()
            self.events.append(event)

    def test_send_email_with_events(self):
        request = self.factory.get('/')
        argv = ['send_email', 'test@example.com', 'Test Subject', 'This is a test message.']
        context = {}

        send_email(request, self.events, argv, context)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        self.assertEqual(mail.outbox[0].body, 'This is a test message.')
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])

    def test_send_email_without_events(self):
        request = self.factory.get('/')
        events = []
        argv = ['send_email', 'test@example.com', 'Test Subject', 'This is a test message.']
        context = {}

        send_email(request, events, argv, context)

        self.assertEqual(len(mail.outbox), 0)
