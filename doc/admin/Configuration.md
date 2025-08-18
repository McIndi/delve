# Configuration

Delve uses the Django configuration system, which involves setting various options in the `settings.py` file. This file contains all the configuration settings for your Delve instance.

## Overview of Django Configuration
Django configuration is typically done in the `settings.py` file, which includes settings for the database, installed apps, middleware, and more. You can also use environment variables to override settings, which is useful for different environments (e.g., development, testing, production).

### Using Environment Variables
To use environment variables in Django, you can use the `os` module to read environment variables and set them in `settings.py`. For example:

```python
import os

DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'delve'),
        'USER': os.getenv('DB_USER', 'delve_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

**NOTE**: The second argument to `os.getenv` is for the default value if the environment variable is not set.

## Configuring Email Settings
Django provides a flexible email backend system that allows you to configure various email settings. Here are the steps to configure email settings in `settings.py`:

### SMTP Email Backend
To use an SMTP server for sending emails, configure the following settings in `settings.py`:

```python
# filepath: /delve/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.your-email-provider.com'
EMAIL_PORT = 587  # Common ports are 587 (TLS) or 465 (SSL)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-app-specific-password'
DEFAULT_FROM_EMAIL = 'Delve Alerts <alerts@your-domain.com>'
```

### File-Based Email Backend
For development purposes, you can use the file-based email backend, which writes emails to a file instead of sending them. Configure the following settings in `settings.py`:

```python
# filepath: /delve/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages'  # Change this to your preferred location
```

## Delve-Specific Configuration Options
Delve has several specific configuration options that you can set in `settings.py`:

- **DELVE_AUTORELOAD**: If `True`, Python source code changes will result in a reload of the server to apply the new code.
- **DELVE_SERVER_HOST**: The host on which to serve the Delve web UI (must also be in `ALLOWED_HOSTS` setting).
- **DELVE_SERVER_PORT**: The TCP port on which to serve the Delve web UI.
- **DELVE_SERVER_LOG_STDOUT**: If `True`, send HTTP server logging to stdout.
- **DELVE_MAX_REQUEST_BODY_SIZE**: The max size in bytes for request body size.
- **DELVE_MAX_REQUEST_HEADER_SIZE**: The max size in bytes for request headers.
- **DELVE_SSL_PRIVATE_KEY**: The TLS Private Key (in PEM format) to use for TLS.
- **DELVE_SSL_CERTIFICATE**: The TLS Certificate (in PEM format) to use for TLS.
- **DELVE_SSL_MODULE**: The SSL module to use with the web server (`builtin` or `openssl`).
- **DELVE_SOCKET_TIMEOUT**: The number of seconds to wait for sockets to be established.
- **DELVE_SOCKET_QUEUE_SIZE**: The number of connections to allow to queue before being rejected.
- **DELVE_ACCEPTED_QUEUE_TIMEOUT**: How long to wait for an HTTP request to be accepted before timing out.
- **DELVE_SERVER_MAX_THREADS**: The max number of threads to spawn to handle web requests.
- **DELVE_ENABLE_EXTRACTIONS_ON_CREATE**: If `True`, Delve will run field extraction functions on events based on sourcetype when the events are created.
- **DELVE_ENABLE_PROCESSORSS_ON_CREATE**: If `True`, Delve will run processor functions on events based on sourcetype when the events are created.
- **DELVE_ENABLE_EXTRACTIONS_ON_UPDATE**: If `True`, Delve will run field extraction functions on events based on sourcetype when the events are updated.
- **DELVE_ENABLE_PROCESSORSS_ON_UPDATE**: If `True`, Delve will run processor functions on events based on sourcetype when the events are updated.
- **DELVE_STRICT_VALIDATION**: (Experimental) If enabled, type checks will be performed on the values passed between search commands, which can cause crashes.
- **DELVE_DOCUMENTATION_DIRECTORY**: The directory where the Delve documentation will be served from.
- **DELVE_EXTRACTION_MAP**: A mapping of sourcetype to field extraction function to be called on each event with the specified sourcetype.
- **DELVE_PROCESSOR_MAP**: A mapping of sourcetype and processor function to be called on each event with the specified sourcetype.
- **DELVE_NAV_MENU**: A mapping of title and view to add to the side nav of the Delve web UI.
- **DELVE_SEARCH_COMMANDS**: A mapping of search commands to their functions.
- **Q_CLUSTER**: Not specific to Delve, but is the task scheduler used by Delve.
- **DELVE_SERVICE_COMMANDS**: The commands specifying the processes for the Delve Supervisor Service to spawn and keep alive.
- **DELVE_SERVICE_INTERVAL**: The number of seconds to sleep before the next check on the processes for the Delve Supervisor Service.

## Example Configuration

Please see the provided `example-settings.py` which can be found in the Delve installation directory at `./delve/example-settings.py` for an example.

---

[Previous: Installation and Setup](Installation_and_Setup.md) | [Next: Ingesting Data](Ingesting_Data.md)
