# Application Developer Guide

This document is for developers looking to build a Delve App to integrate one or more data sources into Delve in a more tailored way than Delve makes possible out-of-the-box.

## Introduction

The most important thing to know about Delve Apps is that they are, at their core, Django Apps. This means that the world-class documentation that Django provides, as well as years of questions and answers on sites like Stack Overflow, applies to Delve as well.

Be sure to review and refer to the [Django documentation](https://docs.djangoproject.com/).

Delve is a data platform designed to be lightweight, easy, versatile, and scalable. Delve is built on Django and Django Rest Framework.

Delve is made up of the following parts:

- **REST API** - A fully-featured and tested REST API providing access to almost all of the data that Delve has.
- **Web UI** - A convenient web interface featuring a dynamic, universal search interface, and a simple navigation bar showing available dashboards.
- **Admin UI** - A one-stop-shop administrative dashboard.
- **CLI Utilities** - Utilities that are useful for Delve but don't fit neatly into the web-server paradigm, like file-tailing and syslog receivers.
- **An Extensible Query Language** - Designed on the idea of shell pipelines, search commands are provided to access and transform data. Queries are parsed according to shell-style semantics but are also rendered in Jinja2 context, providing templating capabilities useful for updating a dashboard panel with a form, for instance.

A custom app can tie into every piece of Delve.

## Creating a Custom Application

To create a Delve application, follow these steps:

1. **Create the Application:**
   Run the following command to create a new Delve application:
   ```bash
   ./fl startapp your_app_name
   ```

2. **Register the Application:**
   Add your new application to the `INSTALLED_APPS` list in `./delve/settings.py`:
   ```python
   # filepath: ./delve/settings.py
   INSTALLED_APPS = [
       # ...existing code...
       'your_app_name',
   ]
   ```

### Creating a Data Model

Creating data models for your app provides a number of benefits. While Delve Events are designed to be a flexible, general-purpose data container, custom data models can be tailored to your specific use case:

- Data is stored in a separate database table.
- Allows custom data permissions.
- Allows binding logic to data in Python.
- Almost automatic forms.
- Almost automatic API endpoints.
- Almost automatic data serializers.
- Almost automatic admin interface integration.
- Almost automatic web interface.
- Custom signal handling when data is added, deleted, updated, etc.

The Django project maintains extensive documentation on models, please refer to that documentation for detailed information on everything about models.

Here is an example model, if you named your app `your_app_name`, the file for models would be `./your_app_name/models.py`:
```python
# filepath: ./your_app_name/models.py
from django.db import models

class MyCustomModel(models.Model):
    str_field = models.CharField(max_length=255)
    text_field = models.TextField()
    int_field = models.IntegerField()
    datetime_field = models.DateTimeField()
    json_field = models.JSONField()
```

### Creating Custom Forms

Forms in Django provide a way to handle user input and validate data. They can be used to create, update, and delete records in your database.

Here is an example form for the `MyCustomModel`:
```python
# filepath: ./your_app_name/forms.py
from django import forms
from .models import MyCustomModel

class MyCustomModelForm(forms.ModelForm):
    class Meta:
        model = MyCustomModel
        fields = ['str_field', 'text_field', 'int_field', 'datetime_field', 'json_field']
```

### Creating Custom Views and Templates

Views in Django handle the logic for your application. They process user input, interact with models, and render templates.

Here is an example view for creating a new `MyCustomModel` instance:
```python
# filepath: ./your_app_name/views.py
from django.shortcuts import render, redirect
from .forms import MyCustomModelForm

def create_my_custom_model(request):
    if request.method == 'POST':
        form = MyCustomModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = MyCustomModelForm()
    return render(request, 'your_app_name/create_my_custom_model.html', {'form': form})
```

Here is an example template for the view:
```html
<!-- filepath: ./your_app_name/templates/your_app_name/create_my_custom_model.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Create My Custom Model</title>
</head>
<body>
    <h1>Create My Custom Model</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Save</button>
    </form>
</body>
</html>
```

### Creating Custom Search Commands

Delve allows you to create custom search commands in Python and register them in `settings.py` under `DELVE_SEARCH_COMMANDS`. This provides powerful and flexible ways to manipulate the result set.

Here is an example of a custom search command:
```python
# filepath: /delve/search_commands/custom_command.py
def custom_command(events, **kwargs):
    # Custom logic to process events
    for event in events:
        event['custom_field'] = 'custom_value'
    return events
```

To register the custom command, add it to `settings.py`:
```python
# filepath: /delve/settings.py
DELVE_SEARCH_COMMANDS = {
    'custom_command': 'delve.search_commands.custom_command.custom_command',
}
```

### Creating Custom Parsers

Parsers in Delve are used to extract fields from events based on their sourcetype. You can create custom parsers to handle specific data formats.

Here is an example of a custom parser:
```python
# filepath: /delve/parsers/custom_parser.py
def custom_parser(event_text):
    # Custom logic to extract fields from event_text
    extracted_fields = {
        'field1': 'value1',
        'field2': 'value2',
    }
    return extracted_fields
```

To register the custom parser, add it to `settings.py`:
```python
# filepath: /delve/settings.py
DELVE_EXTRACTION_MAP = {
    'custom_sourcetype': 'delve.parsers.custom_parser.custom_parser',
}
```

### Creating Custom Processors

Processors in Delve are used to process events based on their sourcetype. You can create custom processors to handle specific processing logic.

Here is an example of a custom processor:
```python
# filepath: /delve/processors/custom_processor.py
def custom_processor(event):
    # Custom logic to process the event
    if 'error' in event.text:
        # Send an alert or perform some action
        pass
    return event
```

To register the custom processor, add it to `settings.py`:
```python
# filepath: /delve/settings.py
DELVE_PROCESSOR_MAP = {
    'custom_sourcetype': 'delve.processors.custom_processor.custom_processor',
}
```

### Creating Custom Management Commands

Django provides a way to create custom management commands that can be run from the command line. These commands can be used to perform various tasks, such as data import/export, maintenance, and more.

Here is an example of a custom management command:
```python
# filepath: ./your_app_name/management/commands/custom_command.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Custom management command'

    def handle(self, *args, **kwargs):
        # Custom logic for the management command
        self.stdout.write('Custom command executed successfully')
```

### Creating Custom Dashboards

Delve allows you to create custom dashboards to visualize your data. Dashboards can include charts, tables, and other visualizations.

Here is an example of a custom dashboard view:
```python
# filepath: ./your_app_name/views.py
from django.shortcuts import render

def custom_dashboard(request):
    # Custom logic to retrieve and process data for the dashboard
    data = {
        'chart_data': [1, 2, 3, 4, 5],
        'table_data': [
            {'column1': 'value1', 'column2': 'value2'},
            {'column1': 'value3', 'column2': 'value4'},
        ],
    }
    return render(request, 'your_app_name/custom_dashboard.html', data)
```

Here is an example template for the custom dashboard:
```html
<!-- filepath: ./your_app_name/templates/your_app_name/custom_dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Custom Dashboard</title>
</head>
<body>
    <h1>Custom Dashboard</h1>
    <div id="chart">
        <!-- Render chart using chart_data -->
    </div>
    <div id="table">
        <table>
            <thead>
                <tr>
                    <th>Column 1</th>
                    <th>Column 2</th>
                </tr>
            </thead>
            <tbody>
                {% for row in table_data %}
                <tr>
                    <td>{{ row.column1 }}</td>
                    <td>{{ row.column2 }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
```

### Creating Custom Alerts and Notifications

Delve provides two methods for implementing alerts: search-based alerts using the `send_email` command and processor-based alerts using the `DELVE_PROCESSOR_MAP`.

#### Search-based Alerts

To create an alert, you'll need to:

1. First, save your query using one of these methods:
   - **Explore UI**: Create and test your query in `/explore`, then click "Save Query"
   - **Django Admin**: Navigate to `/admin/events/query/` and create a new Query
   - **REST API**: POST to `/api/queries/`

Example query to save:
```bash
search --last-15-minutes text__icontains=fail index=logs
| qs_values host
| qs_annotate count=Count(host)
| qs_order_by count
| qs_filter count__gt=100
| send_email to="team@example.com" subject="High Failure Rate Alert"
```

2. Schedule the saved query using Django Q:
   1. Ensure the Q cluster is running (`fl qcluster` or via Windows Service)
   2. Access the Django admin interface at `/admin/`
   3. Navigate to `Django Q > Scheduled tasks`
   4. Click "Add Scheduled task"
   5. Configure the schedule:
      ```python
      Name: "High Error Rate Alert"
      Func: "events.util.run_query"
      Hook: None
      Args: '["High Error Rate Alert"]'  # Use your saved query name here
      Schedule Type: CRON
      Cron: */15 * * * *  # Runs every 15 minutes
      ```
   6. Set additional options:
      - `Repeats`: -1 for infinite repetition
      - `Next Run`: When the schedule should start
      - `Cluster`: Leave as default

Note: For Windows installations using the Delve service, make sure the service is running to process scheduled tasks (ie. make sure a `qcluster` command is included DELVE_SERVICE_COMMANDS). You can check the service status in Windows Services (services.msc).

#### Processor-based Alerts

For immediate alerts when specific events are ingested, use the `DELVE_PROCESSOR_MAP`:

```python
# filepath: /delve/settings.py
def alert_on_critical_error(event):
    from django.core.mail import send_mail
    
    if 'CRITICAL' in event.upper():
        send_mail(
            subject='Critical Error Detected',
            message=f'Critical error in event: {event.id}',
            from_email='alerts@your-domain.com',
            recipient_list=['team@example.com'],
        )

DELVE_PROCESSOR_MAP = {
    'error_logs': alert_on_critical_error,
    'security_events': 'myapp.processors.security_alert_processor',
}
```

The processor function is called whenever an event with the matching sourcetype is created or updated. This allows for real-time alerting based on event content.

### Security and Permissions

When accessing data from custom search commands and other sources of untrusted data, it is crucial to consider security and permissions. Always validate and sanitize input data to prevent security vulnerabilities such as SQL injection, cross-site scripting (XSS), and other attacks.

Here are some best practices for ensuring security and permissions:

- **Validate Input Data**: Always validate and sanitize input data to ensure it meets the expected format and constraints.
- **Use Django's Built-in Security Features**: Django provides several built-in security features, such as CSRF protection, XSS protection, and SQL injection prevention. Make sure to use these features in your application.
- **Implement Proper Access Controls**: Ensure that only authorized users have access to sensitive data and functionality. Use Django's authentication and authorization system to manage user permissions.
- **Raise Descriptive Exceptions**: When something goes wrong, raise descriptive exceptions to provide meaningful error messages. This helps with debugging and ensures that users understand what went wrong.

### Writing Reusable Apps

Writing reusable apps is a key aspect of developing with Django and Delve. Reusable apps can be shared across multiple projects, making it easier to maintain and extend functionality.

Here are some tips for writing reusable apps:

- **Follow Django's App Structure**: Organize your app according to Django's recommended app structure. This makes it easier to understand and maintain.
- **Use Namespaces**: Use namespaces for your app's models, views, templates, and static files to avoid conflicts with other apps.
- **Document Your Code**: Provide clear and comprehensive documentation for your app, including installation instructions, usage examples, and configuration options.
- **Write Tests**: Write tests for your app to ensure that it works as expected and to catch any regressions. Use Django's testing framework to write unit tests, integration tests, and functional tests.
- **Consider Dependencies**: Minimize dependencies on other apps and libraries to make your app more portable. If your app depends on other libraries, clearly document these dependencies and provide installation instructions.

By following these guidelines, you can create powerful and flexible Delve apps that integrate seamlessly with the platform and provide valuable functionality to users.

---

[Previous: User Guide](User_Guide.md) | [Next: API Reference](API_Reference.md)
