# Advanced Logging

## Introduction
This section provides detailed information on configuring Python's logging system for use with Django, Django REST framework, Django Q, and Delve. Proper logging is crucial for monitoring application behavior, debugging issues, and maintaining security.

## Table of Contents
1. [Configuring Python Logging](#configuring-python-logging)
2. [Log Formatters](#log-formatters)
   - [Including Process and Thread IDs](#including-process-and-thread-ids)
   - [Including Filename and Line Number](#including-filename-and-line-number)
3. [Significant Loggers](#significant-loggers)
   - [Django SQL Logger](#django-sql-logger)
   - [Django Request Logger](#django-request-logger)
4. [Advanced Handlers](#advanced-handlers)
   - [SMTPHandler](#smtphandler)
   - [TimedRotatingFileHandler](#timedrotatingfilehandler)
5. [Example Configuration](#example-configuration)

## Configuring Python Logging
To configure logging in a Django project, you typically modify the `LOGGING` dictionary in your `settings.py` file. This dictionary defines the formatters, handlers, and loggers used by the application.

```python
# settings.py
logging.config.dictConfig(
    {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
            'file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': 'debug.log',
                'when': 'midnight',
                'backupCount': 7,
                'formatter': 'verbose',
            },
            'mail_admins': {
                'class': 'django.utils.log.AdminEmailHandler',
                'level': 'ERROR',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
            },
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }
)
```

## Log Formatters

### Including Process and Thread IDs
To include process and thread IDs in your log messages, you can use the `process` and `thread` attributes in your formatter configuration.

```python
'formatters': {
    'verbose': {
        'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
        'style': '{',
    },
}
```

### Including Filename and Line Number
To include the filename and line number in your log messages, use the `pathname` and `lineno` attributes.

```python
'formatters': {
    'detailed': {
        'format': '{levelname} {asctime} {pathname} {lineno:d} {message}',
        'style': '{',
    },
}
```

## Significant Loggers

### Django SQL Logger
The `django.db.backends` logger logs all SQL queries executed by Django. This can be useful for debugging performance issues or understanding the database interactions of your application.

```python
'loggers': {
    'django.db.backends': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    },
}
```

### Django Request Logger
The `django.request` logger logs all HTTP requests processed by Django. This is useful for monitoring request handling and identifying issues with specific requests.

```python
'loggers': {
    'django.request': {
        'handlers': ['mail_admins'],
        'level': 'ERROR',
        'propagate': False,
    },
}
```

## Advanced Handlers

### SMTPHandler
The `SMTPHandler` sends log messages via email. This is useful for alerting administrators to critical issues.

```python
'handlers': {
    'mail_admins': {
        'class': 'logging.handlers.SMTPHandler',
        'mailhost': ('smtp.example.com', 587),
        'fromaddr': 'server-error@example.com',
        'toaddrs': ['admin@example.com'],
        'subject': 'Application Error',
        'credentials': ('username', 'password'),
        'secure': (),
    },
}
```

### TimedRotatingFileHandler
The `TimedRotatingFileHandler` rotates log files at a specified interval, such as daily or weekly. This helps manage log file sizes and keeps logs organized.

```python
'handlers': {
    'file': {
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': 'debug.log',
        'when': 'midnight',
        'backupCount': 7,
        'formatter': 'verbose',
    },
}
```

## Example Configuration
Here is an example configuration that combines the elements discussed above.

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'detailed': {
            'format': '{levelname} {asctime} {pathname} {lineno:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'debug.log',
            'when': 'midnight',
            'backupCount': 7,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'class': 'logging.handlers.SMTPHandler',
            'mailhost': ('smtp.example.com', 587),
            'fromaddr': 'server-error@example.com',
            'toaddrs': ['admin@example.com'],
            'subject': 'Application Error',
            'credentials': ('username', 'password'),
            'secure': (),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

This configuration ensures that log messages are properly formatted, significant events are logged, and critical issues are communicated to administrators.
