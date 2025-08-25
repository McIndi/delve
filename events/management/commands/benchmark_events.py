# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection, transaction
from django.contrib.auth import get_user_model
import time
import statistics
from events.models import Event
from events.serializers import EventSerializer

class Command(BaseCommand):
    help = 'Benchmark Event model operations'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a test user for the benchmarks
        User = get_user_model()
        self.test_user, _ = User.objects.get_or_create(
            username='benchmark_user',
            defaults={'email': 'benchmark@example.com'}
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting benchmark...\n')
        
        # Test configurations
        batch_sizes = [1, 100, 1000]
        iterations = 5

        results = {
            'insert': {},
            'retrieve': {},
            'range_query': {}
        }

        for batch_size in batch_sizes:
            self.stdout.write(f'\nTesting batch size: {batch_size}')
            insert_times = []
            retrieve_times = []
            range_times = []

            for i in range(iterations):
                # Clear Django's query cache
                connection.queries_log.clear()

                # Measure insert performance
                start = time.time()
                with transaction.atomic():
                    self._create_batch(batch_size)
                insert_times.append(time.time() - start)

                # Measure retrieval performance
                start = time.time()
                self._retrieve_latest(batch_size)
                retrieve_times.append(time.time() - start)

                # Measure range query performance
                start = time.time()
                self._range_query()
                range_times.append(time.time() - start)

            results['insert'][batch_size] = statistics.mean(insert_times)
            results['retrieve'][batch_size] = statistics.mean(retrieve_times)
            results['range_query'][batch_size] = statistics.mean(range_times)

        self._print_results(results)

    def _create_batch(self, size):
        data = [
            {
                'text': f'test event {i}',
                'source': 'benchmark',
                'sourcetype': 'test'
            } for i in range(size)
        ]
        # Create serializer context with mock request
        context = {
            'request': type('MockRequest', (), {'user': self.test_user})()
        }
        serializer = EventSerializer(data=data, many=True, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def _retrieve_latest(self, count):
        # Force evaluation of queryset with list()
        return list(Event.objects.order_by('-created')[:count])

    def _range_query(self):
        # For current UUID-based model, use created field
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Force evaluation of queryset with list()
        return list(Event.objects.filter(created__gte=start_of_month))

    def _print_results(self, results):
        self.stdout.write('\n=== BENCHMARK RESULTS ===\n')
        for operation, sizes in results.items():
            self.stdout.write(f'\n{operation.upper()} PERFORMANCE:')
            for batch_size, avg_time in sizes.items():
                self.stdout.write(
                    f'Batch size {batch_size}: {avg_time:.4f} seconds '
                    f'({batch_size/avg_time:.2f} operations/second)'
                )