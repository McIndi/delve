"""Regression coverage for sandboxed search-query templates."""

import json
import sys
from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.urls import reverse
from jinja2.exceptions import SecurityError
from rest_framework.test import APITestCase

from events.models import GlobalContext, LocalContext, Query
from events.util import run_query


class QueryTemplateSandboxTests(APITestCase):
    ESCAPES = (
        "{{ ''.__class__.__mro__[1].__subclasses__() }}",
        "{{ cycler.__init__.__globals__ }}",
        "{{ joiner.__init__.__globals__['__builtins__'] }}",
        "{{ namespace.__init__.__globals__ }}",
    )

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='template-user')
        self.request = MagicMock(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_saved_queries_reject_chained_escapes_before_later_commands(self):
        for payload in self.ESCAPES:
            with self.subTest(payload=payload):
                query = Query.objects.create(
                    user=self.user,
                    text=f'echo "{payload}" | set reached=true | echo later',
                )
                context = {}
                stdout, stderr = sys.stdout, sys.stderr
                with self.assertRaises(SecurityError):
                    query.resolve(request=self.request, context=context)
                self.assertEqual(context, {})
                self.assertIs(sys.stdout, stdout)
                self.assertIs(sys.stderr, stderr)

    def test_resolve_endpoint_returns_security_error_without_command_output(self):
        for payload in self.ESCAPES:
            with self.subTest(payload=payload):
                response = self.client.post(
                    reverse('api_query'),
                    {'text': f'echo "{payload}" | echo later'},
                    format='json',
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(len(data), 1)
                self.assertEqual(set(data[0]), {'exception'})
                self.assertIn('SecurityError', data[0]['exception'])
                self.assertNotIn('<class', data[0]['exception'])

    def test_run_query_rejects_saved_escape(self):
        query = Query.objects.create(
            name='unsafe-template', user=self.user,
            text=f'echo "{self.ESCAPES[0]}"',
        )
        with self.assertRaises(SecurityError):
            run_query(query.id)

    def test_single_unsafe_attribute_does_not_expose_python_internals(self):
        results = Query(user=self.user, text='echo "{{ lipsum.__globals__ }}"').resolve(
            request=self.request,
        )
        self.assertEqual(results, [{'expression': ''}])

    def test_global_and_local_context_filters_blocks_and_missing_variables(self):
        GlobalContext.objects.update_or_create(user=self.user, defaults={'context': {'prefix': 'global'}})
        self.user.refresh_from_db()
        local = LocalContext.objects.create(
            user=self.user, name='template-context',
            context={'values': ['one', 'two'], 'enabled': True},
        )
        query = Query(
            user=self.user,
            text='echo "{% if enabled %}{{ prefix||upper }}:{% for value in values %}'
                 '{{ value }} {% endfor %}{{ absent||default("fallback") }}{% endif %}"',
        )
        self.assertEqual(
            query.resolve(request=self.request, context=local.name),
            [{'expression': 'GLOBAL:one two fallback'}],
        )
        query.text = 'echo "{{ prefix }}:{{ local }}:{{ absent }}"'
        self.assertEqual(
            query.resolve(request=self.request, context={'local': 'value'}),
            [{'expression': 'global:value:'}],
        )
        response = self.client.post(
            reverse('api_query'),
            {'text': query.text, 'local_context': json.dumps({'local': 'api'})},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{'expression': 'global:api:'}])

    def test_set_context_remains_available_to_later_templates(self):
        results = Query(user=self.user, text='set foo=bar | echo {{ foo }}').resolve(
            request=self.request,
        )
        self.assertEqual(results, [{'expression': 'bar'}])
