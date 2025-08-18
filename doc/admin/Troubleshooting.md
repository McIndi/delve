# Troubleshooting

Troubleshooting is an essential part of maintaining a Delve instance. This section covers common troubleshooting techniques for Delve, Django, Django Rest Framework, and Django Extensions.

## Common Issues and Solutions
Here are some common issues you might encounter and their solutions:

- **Server Not Starting**: Check the logs for error messages. Ensure that all required services (e.g., database) are running.
- **Database Connection Issues**: Verify the database settings in `settings.py`. Ensure that the database server is running and accessible.
- **Permission Errors**: Ensure that the user running the Delve server has the necessary permissions to access files and directories.
- **Missing Migrations**: Run `fl showmigrations` and `fl migrate` to ensure that all database migrations are applied.
- **Queries Running Slowly**: Check `settings.py` to ensure that DEBUG is set to False and that Debug level logging is not enabled.

## Using Django Debug Toolbar
The Django Debug Toolbar, which comes pre-installed but disabled, is a helpful tool for debugging and profiling Django applications. To enable it, follow these steps:

1. Set `DEBUG` to True:
   ```python
   DEBUG = True
   ```

2. Configure the internal IPs in `settings.py`:
   ```python
   INTERNAL_IPS = ['127.0.0.1']
   ```

**Note**: The Django Debug Toolbar can be misleading because it only really engages during page loads, so AJAX calls (like submitting a search in the Explore UI) may not show in the results. To see the Debug Toolbar with information relevant to the Query, you can enable the Debug Toolbar and navigate to `/api/query` and submit your query in JSON format (ie. `{"text": "search --last-15-minutes"}`).

## Using Django Extensions
Django Extensions provides additional management commands and utilities for Django projects. Django Extensions are installed and enabled by default in Delve.

Some useful commands include:
   - **`./fl shell_plus`**: An enhanced version of the Django shell with autoloading of models and other conveniences.
     ```bash
     fl shell_plus
     ```
   - **`./fl graph_models`**: Creates a GraphViz dot file (or JSON file) for the specified app names.
     ```bash
     fl graph_models events
     ```

## Checking Logs
Regularly check the application logs for errors, warnings, and other important messages.

Logs for the web server and qcluster can be found in the `log` directory, while logs from the utility commands (ie. `syslog-receiver`) will be found in `./utilities/log/`.

You can also configure logging settings in `settings.py` to customize log levels, formats, and handlers. See [Advanced Logging](Advanced_Logging.md) for more details.

## Accessing Support Resources
If you encounter issues that you cannot resolve, consider accessing support resources such as:

- **Django Documentation**: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- **Django Rest Framework Documentation**: [https://www.django-rest-framework.org/](https://www.django-rest-framework.org/)
- **Django Extensions Documentation**: [https://django-extensions.readthedocs.io/](https://django-extensions.readthedocs.io/)
- **Delve Documentation**: Included with every Delve documentation in the `doc` directory, available in the Delve Web UI (default http://127.0.0.1:8000/docs/) and in the [Github Repository](https://github.com/DelveCorp/delve/blob/main/src/home/doc/index)
- **Delve Community**: Refer our [Github Repository](https://github.com/DelveCorp/delve) for reporting issues, submitting feature requests, and contacting the project maintainers.

By following these troubleshooting techniques and utilizing available resources, you can effectively diagnose and resolve issues with your Delve instance.

---

[Previous: Security](Security.md) | [Next: Performance Tuning](Performance_Tuning.md)
