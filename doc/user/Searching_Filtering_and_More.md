# Searching, Filtering and More

Delve provides a comprehensive search interface that supports a wide range of search commands and the ability to define custom search commands. These commands are categorized into four types: Data Sources, Queryset Transformations, Generic Transformations, and Visualization Commands.

## Data Sources
Data source commands are used to pull data into your results. These commands retrieve data from various sources and integrate it into the Delve platform.

### Example Commands

- `search`: Retrieve data through Delve, including the models of registered apps.
- `request`: Perform an HTTP request and return the data.
- `read_file`: Retrieve data from an uploaded file.

## Queryset Transformations
Queryset transformation commands act on Django Querysets (such as the output of the `search` command) and expose Queryset methods. These commands allow you to directly affect the SQL statements before they are executed, resulting in faster performance.

### Example Commands

- `qs_filter`: Filter the queryset based on specified criteria.
- `qs_explain`: Explain the queryset execution plan.
- `qs_latest`: Retrieve the latest entry in the queryset.
- `qs_first`: Retrieve the first entry in the queryset.
- `qs_earliest`: Retrieve the earliest entry in the queryset.
- `qs_count`: Count the number of entries in the queryset.

## Generic Transformations

Generic transformation commands modify data from a source command in some way. These commands are designed to be versatile and work well with diverse sets of data, although they may be slower than their `qs_` counterparts.

### Example Commands

- `rename`: Rename fields in the result set.
- `replace`: Replace values in the result set.
- `rex`: Extract fields using regular expressions.
- `dedup`: Remove duplicate entries from the result set.
- `sort`: Sort the result set based on specified criteria.

## Visualization Commands
Visualization commands take a result set and generate a table, chart, or other visualization. These commands help you to display your data in a meaningful and interactive way.

### Example Commands

- `chart`: Generate a chart based on the result set.
- `table`: Generate a table based on the result set.

## Queryset Grouping
The `qs_group_by` command allows you to group records from a QuerySet based on specified fields and expressions. This command is useful for aggregating data and performing calculations on grouped records.

### Example Commands

- `qs_group_by`: Group records based on specified fields and expressions.

### Example Usage
Here are some example commands to use the `qs_group_by` functionality:

```bash
# Group records by a single field and calculate the average of another field
search index=test | qs_group_by extracted_fields__foo avg_bar=Avg(Cast(extracted_fields__bar, IntegerField))

# Group records by multiple fields and count the number of records in each group
search index=test | qs_group_by extracted_fields__foo extracted_fields__bar count=Count('id')

# Group records by a field and filter the groups based on an aggregate condition
search index=test | qs_group_by extracted_fields__foo avg_bar=Avg(Cast(extracted_fields__bar, IntegerField)) | qs_having avg_bar__gt=1
```

### Explanation

- `qs_group_by extracted_fields__foo avg_bar=Avg(Cast(extracted_fields__bar, IntegerField))`: Groups records by the `extracted_fields__foo` field and calculates the average of the `extracted_fields__bar` field, casting it to an integer.
- `qs_group_by extracted_fields__foo extracted_fields__bar count=Count('id')`: Groups records by the `extracted_fields__foo` and `extracted_fields__bar` fields and counts the number of records in each group.
- `qs_group_by extracted_fields__foo avg_bar=Avg(Cast(extracted_fields__bar, IntegerField)) | qs_having avg_bar__gt=1`: Groups records by the `extracted_fields__foo` field, calculates the average of the `extracted_fields__bar` field, and filters the groups to include only those with an average greater than 1.

The `qs_group_by` command is a powerful tool for aggregating and analyzing data within Delve, allowing you to perform complex queries and calculations on grouped records.

## Difference between Events and events

When talking about Queries in Delve, we can distinguish between `Event` instances, which are `Event`s stored in the database, and 'events' as the unit of data passed between search commands within the context of a Query execution.

Let's take a look at an example:

```bash
search --last-15-minutes index=default
| select extracted_fields
| explode extracted_fields
```

In this example, we start with the same result set that was produced with the previous query, but now the results of the `search` search command have been passed to the `select` search command.

The `select` search command is used to select which fields from the events to keep. The result of this `select` will be that all fields other than `extracted_fields` will be dropped.

The `explode` search command is used to take a field that contains key-value pairs and expand that object to several fields, one for each key-value pair at the top.

So, as you can see, the 'events' passed between the search commands can contain fields other than those of the `Event` instances.

## Example Usage
Here are some example commands to use the search functionality:

```bash
# Basic search to retrieve data from the Delve database  
search --index default text__icontains="error"

# Perform an HTTP request and return the data
request GET https://api.example.com/data

# Retrieve data from an uploaded file
read_file example.xml

# Filter the queryset based on specified criteria
qs_filter field1=value1

# Rename a field in the result set
rename --from-field old_field --to-field new_field

# Generate a bar chart with specified X and Y fields
chart --type bar --x-field date --y-field count
```

## Using Pipe Characters to Create Pipelines
Delve allows you to chain multiple search commands together using the pipe character `|`. This creates a pipeline where the output of one command is passed as input to the next command. For example:

```bash
search --index default text__icontains="error" | rename --from-field old_field --to-field new_field | chart --type bar --x-field date --y-field count
```

In this example, the `search` command retrieves data, the `rename` command renames a field, and the `chart` command generates a bar chart based on the result set.

## Jinja2 Templating
Delve supports Jinja2 templating for search commands. This allows you to dynamically generate search commands based on context variables. The context is built by merging the user's GlobalContext and the LocalContext included in the request. For example:

```bash
search --index {{ index }} text__icontains="{{ keyword }}"
```

In this example, `{{ index }}` and `{{ keyword }}` are Jinja2 template variables that will be replaced with their corresponding values from the context.

This can be useful for including different sets of arguments to the same search command to get different results or behavior. It can also be used with the `query_table` and `query_chart` templatetags which accept Django Form instances for use in dashboards and control panels.

## send_email Command
The `send_email` command allows you to send email notifications based on the result set. This command is configured using Django's SMTP settings. For example:

```bash
search --index default text__icontains="error" | send_email to="team@example.com" subject="Error Alert"
```

In this example, the `send_email` command sends an email to `team@example.com` with the subject "Error Alert" if the search command finds any errors.

## make_events Command
The `make_events` command allows you to generate events based on the current result set and index them into the Delve database. This command is useful for creating new events from existing data or external sources gathered with other search commands like `request`.

### Command-line Arguments
The `make_events` command accepts the following command-line arguments:

- `-i, --index`: The index to assign to the new events. You can use dollar sign notation to assign the value of a field.
- `-o, --host`: The host to assign to the new events. You can use dollar sign notation to assign the value of a field.
- `-s, --source`: The source to assign to the new events. You can use dollar sign notation to assign the value of a field.
- `-t, --sourcetype`: The sourcetype to assign to the new events. You can use dollar sign notation to assign the value of a field.
- `-S, --save`: If specified, the events will be saved.
- `-d, --drop`: If specified, provide the name of a field to drop before creating the events.

### Example Usage
Here are some example commands to use the `make_events` command:

```bash
# Generate events with default settings
make_events

# Specify a custom index and host
make_events --index "custom_index" --host "custom_host"

# Drop specific fields before creating events
make_events --drop "field1" --drop "field2"

# Save the generated events
make_events --save
```

## Custom Search Commands
Delve allows you to create custom search commands in Python and register them in `settings.py` under `DELVE_SEARCH_COMMANDS`. This provides powerful and flexible ways to manipulate the result set.

### Example Custom Command
Here is an example of a custom search command:

```python
# filepath: /delve/search_commands/custom_command.py
def custom_command(events, **kwargs):
    # Custom logic to process events
    for event in events:
        event['custom_field'] = 'custom_value'
    return events
```

Alternatively, you could write it as a generator which could possibly improve memory usage:

```python
# filepath: /delve/search_commands/custom_command.py
def custom_command(events, **kwargs):
    # Custom logic to process events
    for event in events:
        event['custom_field'] = 'custom_value'
        yield event
```
To register the custom command, add it to `settings.py`:

```python
# filepath: /delve/settings.py
DELVE_SEARCH_COMMANDS = {
    ...
    'custom_command': 'delve.search_commands.custom_command.custom_command',
    ...
}
```

## Queryset Search Commands

The `qs_*` commands are designed to modify a Django QuerySet using methods on that QuerySet. These commands allow you to perform various operations such as filtering, annotating, aggregating, and more. The arguments for these commands are parsed in a special way to allow for complex expressions and function calls.

### Argument Parsing

When you use `qs_*` commands, the arguments are parsed into expressions that Django can understand. This means you can use functions and complex expressions to manipulate your data.

### Special Functions

There are some special functions that are particularly useful for searching, transforming, and visualizing your data:

- `F`: Represents the value of a model field. This is useful for referencing fields in expressions, such as when you want to compare or perform operations on fields.
  ```python
  qs_annotate new_field=F('field_name')
  ```
- `Value`: Wraps a value for use in expressions. This is useful for including static values in your expressions.
  ```python
  qs_annotate value_field=Value('static_value')
  ```
- `Q`: Encapsulates a collection of keyword arguments for complex queries. This is useful for building complex filter conditions.
  ```python
  qs_filter Q(field1__gt=10) || Q(field2__lt=5)
  ```
- `KT`: Represents a key transformation. This is useful for transforming keys in JSON fields.
  ```python
  qs_annotate transformed_key=KT('json_field__key__1__foobar')
  ```

#### Available Functions

Here are some functions you can use in your expressions:

- `Lower`: Converts a string to lowercase.
  ```python
  qs_annotate new_field=Lower(old_field)
  ```
- `Upper`: Converts a string to uppercase.
  ```python
  qs_annotate new_field=Upper(old_field)
  ```
- `Length`: Returns the length of a string.
  ```python
  qs_annotate length_field=Length(old_field)
  ```
- `Trim`: Trims whitespace from both ends of a string.
  ```python
  qs_annotate trimmed_field=Trim(old_field)
  ```
- `Cast`: Casts a value to a specified type.
  ```python
  qs_annotate casted_field=Cast(old_field,IntegerField)
  ```
- `Coalesce`: Returns the first non-null value in a list of expressions.
  ```python
  qs_annotate coalesced_field=Coalesce(field1, field2, Value('default'))
  ```
- `Concat`: Concatenates two or more strings.
  ```python
  qs_annotate concatenated_field=Concat(field1, Value(' '), field2)
  ```
- `Greatest`: Returns the greatest value from a list of expressions.
  ```python
  qs_annotate greatest_field=Greatest(field1, field2)
  ```
- `Least`: Returns the least value from a list of expressions.
  ```python
  qs_annotate least_field=Least(field1, field2)
  ```
- `LPad`: Pads a string on the left with a specified character.
  ```python
  qs_annotate lpad_field=LPad(field, 10, fill_text=Value('O'))
  ```
- `RPad`: Pads a string on the right with a specified character.
  ```python
  qs_annotate rpad_field=RPad(field, 10, fill_text=Value('O'))
  ```
- `LTrim`: Trims whitespace from the left end of a string.
  ```python
  qs_annotate ltrim_field=LTrim(field)
  ```
- `RTrim`: Trims whitespace from the right end of a string.
  ```python
  qs_annotate rtrim_field=RTrim(field)
  ```
- `Substr`: Returns a substring from a string.
  ```python
  qs_annotate substr_field=Substr(field, 1, 5)
  ```
- `Replace`: Replaces occurrences of a substring within a string.
  ```python
  qs_annotate replaced_field=Replace(field, Value('old'), Value('new'))
  ```
- `Reverse`: Reverses a string.
  ```python
  qs_annotate reversed_field=Reverse(field)
  ```
- `Now`: Returns the current date and time.
  ```python
  qs_annotate now_field=Now()
  ```
- `TruncDate`: Truncates a date to the specified precision.
  ```python
  qs_annotate trunc_date_field=TruncDate(field)
  ```
- `TruncMonth`: Truncates a date to the month.
  ```python
  qs_annotate trunc_month_field=TruncMonth(field)
  ```
- `TruncYear`: Truncates a date to the year.
  ```python
  qs_annotate trunc_year_field=TruncYear(field)
  ```
- `StrIndex`: Returns the index of a substring within a string.
  ```python
  qs_annotate str_index_field=StrIndex(field, Value('substring'))
  ```
- `Abs`: Returns the absolute value of a number.
  ```python
  qs_annotate abs_field=Abs(field)
  ```
- `ATan2`: Returns the arctangent of two numbers.
  ```python
  qs_annotate atan2_field=ATan2(field1, field2)
  ```
- `Ceil`: Returns the smallest integer greater than or equal to a number.
  ```python
  qs_annotate ceil_field=Ceil(field)
  ```
- `Cos`: Returns the cosine of a number.
  ```python
  qs_annotate cos_field=Cos(field)
  ```
- `Cot`: Returns the cotangent of a number.
  ```python
  qs_annotate cot_field=Cot(field)
  ```
- `Degrees`: Converts radians to degrees.
  ```python
  qs_annotate degrees_field=Degrees(field)
  ```
- `Exp`: Returns the exponential of a number.
  ```python
  qs_annotate exp_field=Exp(field)
  ```
- `Floor`: Returns the largest integer less than or equal to a number.
  ```python
  qs_annotate floor_field=Floor(field)
  ```
- `Ln`: Returns the natural logarithm of a number.
  ```python
  qs_annotate ln_field=Ln(field)
  ```
- `Log`: Returns the logarithm of a number.
  ```python
  qs_annotate log_field=Log(field)
  ```
- `Mod`: Returns the remainder of a division.
  ```python
  qs_annotate mod_field=Mod(field1, field2)
  ```
- `Pi`: Returns the value of pi.
  ```python
  qs_annotate pi_field=Pi()
  ```
- `Power`: Returns a number raised to a power.
  ```python
  qs_annotate power_field=Power(field, 2)
  ```
- `Radians`: Converts degrees to radians.
  ```python
  qs_annotate radians_field=Radians(field)
  ```
- `Round`: Rounds a number to the nearest integer.
  ```python
  qs_annotate round_field=Round(field)
  ```
- `Sign`: Returns the sign of a number.
  ```python
  qs_annotate sign_field=Sign(field)
  ```
- `Sin`: Returns the sine of a number.
  ```python
  qs_annotate sin_field=Sin(field)
  ```
- `Sqrt`: Returns the square root of a number.
  ```python
  qs_annotate sqrt_field=Sqrt(field)
  ```
- `Tan`: Returns the tangent of a number.
  ```python
  qs_annotate tan_field=Tan(field)
  ```
- `Trunc`: Truncates a date to the specified precision. ()
  ```python
  qs_annotate trunc_field=Trunc(field,kind='minute')
  ```
- `Extract`: Extracts a part of a date.
  ```python
  qs_annotate extract_field=Extract(field, 'year')
  ```
- `ExtractDay`: Extracts the day from a date.
  ```python
  qs_annotate extract_day_field=ExtractDay(field)
  ```
- `ExtractHour`: Extracts the hour from a date.
  ```python
  qs_annotate extract_hour_field=ExtractHour(field)
  ```
- `ExtractMinute`: Extracts the minute from a date.
  ```python
  qs_annotate extract_minute_field=ExtractMinute(field)
  ```
- `ExtractMonth`: Extracts the month from a date.
  ```python
  qs_annotate extract_month_field=ExtractMonth(field)
  ```
- `ExtractQuarter`: Extracts the quarter from a date.
  ```python
  qs_annotate extract_quarter_field=ExtractQuarter(field)
  ```
- `ExtractSecond`: Extracts the second from a date.
  ```python
  qs_annotate extract_second_field=ExtractSecond(field)
  ```
- `ExtractWeek`: Extracts the week from a date.
  ```python
  qs_annotate extract_week_field=ExtractWeek(field)
  ```
- `ExtractWeekDay`: Extracts the weekday from a date.
  ```python
  qs_annotate extract_weekday_field=ExtractWeekDay(field)
  ```
- `ExtractYear`: Extracts the year from a date.
  ```python
  qs_annotate extract_year_field=ExtractYear(field)
  ```

#### Aggregation Functions

You can also use these aggregation functions in your expressions:

- `Sum`: Returns the sum of the values.
  ```python
  qs_aggregate total=Sum(field)
  ```
- `Avg`: Returns the average of the values.
  ```python
  qs_aggregate average=Avg(field)
  ```
- `Count`: Returns the count of the values.
  ```python
  qs_aggregate count=Count(field)
  ```
- `Max`: Returns the maximum value.
  ```python
  qs_aggregate max_value=Max(field)
  ```
- `Min`: Returns the minimum value.
  ```python
  qs_aggregate min_value=Min(field)
  ```
- `StdDev`: Returns the standard deviation of the values.
  ```python
  qs_aggregate stddev=StdDev(field)
  ```
- `Variance`: Returns the variance of the values.
  ```python
  qs_aggregate variance=Variance(field)
  ```

#### Example Usages

Here are some example usages of the `qs_*` commands, starting with the `search` command and using multiple `qs_*` commands to manipulate the result set.

```bash
# Search for events and annotate them with additional fields
search field1=value1 | qs_annotate new_field1=Lower(old_field1) new_field2=Concat(field2, Value('suffix'))

# Search for events, filter them, and then count the results
search field1=value1 | qs_filter field2__gt=10 | qs_count

# Search for events, aggregate them, and then annotate the results
search field1=value1 | qs_aggregate total=Sum(field2) average=Avg(field2) | qs_annotate new_field=F('total') + F('average')

# Search for events and retrieve dates from the queryset
search field1=value1 | qs_dates field=date_field kind=month order=ASC
```

### Notes

The `qs_*` commands use Django's ORM methods to perform the specified operations on the QuerySet. The arguments are parsed into expressions that Django can understand, allowing for complex expressions and function calls to be used in the arguments. This provides powerful and flexible ways to manipulate the result set.

---

[Previous: Ingesting Data](Ingesting_Data.md) | [Next: Alerts and Notifications](Alerts_and_Notifications.md)
