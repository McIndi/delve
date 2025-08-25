# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from multiprocessing import cpu_count
import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import cherrypy

from delve.wsgi import application

cherrypy_log = logging.getLogger("")
cherrypy_log.setLevel(logging.INFO)

class Command(BaseCommand):
    help = "Use cherrypy to serve the web app"

    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--max-threads",
            default=settings.DELVE_SERVER_MAX_THREADS,
            type=int,

        )
        parser.add_argument(
            '--auto-reload',
            action='store_true',
            help='reload on changes to the code.'
        )
        parser.add_argument(
            '--host',
            default=settings.DELVE_SERVER_HOST,
            help='The host to serve',
        )
        parser.add_argument(
            '--port',
            default=settings.DELVE_SERVER_PORT,
            help='The port to serve',
        )
        parser.add_argument(
            '--log-stdout',
            action='store_true',
            help='If specified, server logs will be sent to stdout',
        )
        parser.add_argument(
            '--max-body-size',
            default=settings.DELVE_MAX_REQUEST_BODY_SIZE,
            help='The maximum allowable request body size',
        )
        parser.add_argument(
            '--max-header-size',
            default=settings.DELVE_MAX_REQUEST_HEADER_SIZE,
            help='The maximum allowable request header size',
        )
        parser.add_argument(
            '--private-key',
            default=settings.DELVE_SSL_PRIVATE_KEY,
            help='filename for ssl private key',
        )
        parser.add_argument(
            '--public-cert',
            default=settings.DELVE_SSL_CERTIFICATE,
            help='filename for ssl public cert',
        )
        parser.add_argument(
            '--socket-timeout',
            default=settings.DELVE_SOCKET_QUEUE_SIZE,
            help='The timeout in seconds for accepted connections',
        )
        parser.add_argument(
            '--socket-queue-size',
            default=settings.DELVE_SOCKET_QUEUE_SIZE,
            help='The maximum number of queued connections'
        )
        parser.add_argument(
            '--accepted-queue-timeout',
            default=settings.DELVE_ACCEPTED_QUEUE_TIMEOUT,
            help='The timeout in seconds for attempting to add a request to the queue when the queue is full'
        )
        # parser.add_argument("-i", "--index")
        # parser.add_argument("-H", "--host")
        # parser.add_argument("-s", "--source", default="user")
        # parser.add_argument("-t", "--sourcetype", default="json")
        

    def handle(self, *args, **options):
        max_threads = options["max_threads"]
        auto_reload = options["auto_reload"] or settings.DELVE_AUTORELOAD
        host = options["host"]
        port = options["port"]
        log_stdout = options["log_stdout"] or settings.DELVE_SERVER_LOG_STDOUT
        max_body_size = options["max_body_size"]
        max_header_size = options["max_header_size"]
        private_key = options["private_key"]
        public_cert = options["public_cert"]
        socket_timeout = options["socket_timeout"]
        socket_queue_size = options["socket_queue_size"]
        accepted_queue_timeout = options["accepted_queue_timeout"]

        try:
            cherrypy.tree.graft(application, "/")
            cherrypy.config.update(
                {
                    'engine.autoreload.on': auto_reload,
                    'log.screen': log_stdout,
                    'server.socket_port': port,
                    'server.socket_host': host,
                    'server.max_request_body_size': max_body_size,
                    'server.max_request_header_size': max_header_size,
                    'server.ssl_private_key': private_key,
                    'server.ssl_module': 'builtin',
                    'server.ssl_certificate': public_cert,
                    'server.socket_timeout': socket_timeout,
                    'server.socket_queue_size': socket_queue_size,
                    'server.accepted_queue_timeout': accepted_queue_timeout,
                    'server.thread_pool': max_threads,
                }
            )
            cherrypy.engine.signal_handler.subscribe()
            if hasattr(cherrypy.engine, 'console_control_handler'):
                cherrypy.engine.console_control_handler.subscribe()
            cherrypy_log.info(f"Serving on {host}:port/")
            cherrypy.engine.start()
            cherrypy.engine.block()
        except KeyboardInterrupt:
            cherrypy_log.info("Shutting down server")
            cherrypy.engine.exit()
        except SystemExit:
            cherrypy_log.info("Shutting down server")
            cherrypy.engine.exit()
        except:
            cherrypy_log.exception("An unhandled exception has ocurred")
            cherrypy.engine.exit()
            raise CommandError("An unhandled exception has ocurred")
        # self.stdout.write(
        #     self.style.SUCCESS(f'Successfully created event "{vars(e)}"')
        # )
