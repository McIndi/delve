# Ingesting Data

Delve supports data ingestion from various sources, including log files, REST APIs, syslog, and more. This guide covers the different methods for ingesting data into Delve and provides detailed instructions for each method.

## Delve's REST API

Delve provides a REST API for data ingestion, allowing you to programmatically send data to the platform. This method is ideal for integrating with other applications and services that generate data.

### Accessing the browsable REST API

To access the browsable REST API, navigate to `/api/` in your browser. You will see a list of available endpoints, including:

- `/api/events/`: Manage events.
- `/api/search_commands/`: Manage search commands.
- `/api/queries/`: Manage queries.
- `/api/globals/`: Manage global contexts.
- `/api/locals/`: Manage local contexts.
- `/api/files/`: Manage file uploads.

#### The `/api/query` Endpoint

While not useful to Ingesting data, the `/api/query` should be mentioned when discussing the Delve REST API as it does not appear in the list of endpoints you see at `/api` from a browser.

This endpoint is provided to allow the resolution of queries.

The `/api/query` endpoint is what is used to power the Explore UI which is available at `/explore`.

The browsable REST API, which is returned when accessing `/api/query` from a browser can be really useful for debugging if you enable `DEBUG` in your `settings.py` as it allows you to track the SQL statements issued by search commands as well as a ton of other useful information.

### Example Usage

To create a new event, send a POST request to `/api/events/` with the following JSON payload:

```json
{
    "text": "Example event text",
    "index": "default",
    "host": "localhost",
    "source": "example_source",
    "sourcetype": "example_sourcetype"
}
```

## File-tail Utility
The file-tail utility allows you to ingest data from log files in near real-time. This utility monitors specified log files and sends new entries to Delve as they are written. This is particularly useful for continuously monitoring log files for new data.

**NOTE**: If a log file is rotated (renamed or moved by the system or a log rotation utility), Delve will automatically detect the change and continue monitoring the new file with the same filename.

### Usage
The file-tail utility is a command-line tool that can be used to monitor log files and send new entries to Delve. Below are the steps to use the file-tail utility:

1. Open a terminal or command prompt.
2. Navigate to the Delve directory.
3. Execute `set-env.bat` (Windows) or `source set-env` (Linux/Mac).
4. Execute `python utilities/cli/tail-files.py --help`.
5. Run the script with the appropriate arguments.

### Command-line Arguments
The `tail-files.py` script accepts the following command-line arguments:

- `--server`: The scheme, host, and port of the Delve server (default: `http://localhost:8000`).
- `--no-verify`: If specified, TLS hostname verification will be disabled.
- `-i, --index`: The index in which to store the event (default: `default`).
- `-H, --host`: The host to associate with the event (default: `localhost`).
- `-t, --sourcetype`: The sourcetype to associate with the event (default: `plaintext`).
- `-u, --username`: The username to use for authentication (if omitted, you will be prompted).
- `-p, --password`: The password to use for authentication (if omitted, you will be prompted).
- `-v, --verbose`: Increase verbosity of log output.
- `-l, --log-file`: The file to which logs will be written (default: `log/tail-files.log`).
- `-d, --delay`: The number of seconds to sleep between API POST requests (default: `1`).
- `--batch-size`: The number of events to send to the Delve server per request (default: `1000`).
- `--max-queue-size`: The maximum number of events waiting to be uploaded to Delve (default: `10000`).
- `patterns`: Glob patterns matching files to monitor (quote this to prevent shell expansion).

### Example Usage
Here are some example commands to use the file-tail utility:

```bash
# Basic usage with default settings
python utilities/cli/tail-files.py "/path/to/logfile.log"

# Specify a custom index
python utilities/cli/tail-files.py --index "my_index" "/path/to/logfile.log"

# Specify a custom sourcetype
python utilities/cli/tail-files.py --sourcetype "my_sourcetype" "/path/to/logfile.log"

# Disable TLS hostname verification for the Delve server
python utilities/cli/tail-files.py --no-verify --server "https://delve.example.com" "/path/to/logfile.log"

# Provide username and password for authentication to prevent being prompted
python utilities/cli/tail-files.py--username "myuser" --password "mypassword" "/path/to/logfile.log"

# Slightly decrease verbosity of log output
python utilities/cli/tail-files.py -v "/path/to/logfile.log"

# Most verbose log output
python utilities/cli/tail-files.py -vvvvvv "/path/to/logfile.log"

# Monitor multiple log files using glob patterns
python utilities/cli/tail-files.py"/var/log/*.log"
```

### Additional Information
The file-tail utility maintains the position of the last read entry in each monitored log file. This information is stored in a JSON file (`utilities/_data/tail-files.json`) to ensure that the utility can resume from where it left off in case of a restart.

The utility batches events to improve performance. You can configure the batch size and the maximum queue size using the `--batch-size` and `--max-queue-size` arguments, respectively.

## Syslog (UDP/TCP/TLS)
Delve supports Syslog for data ingestion over UDP, TCP, and TCP with TLS. This method is commonly used for collecting logs from network devices, servers, and other infrastructure components.

### Usage
The syslog-receiver utility is a command-line tool that can be used to receive syslog messages and send them to Delve. Below are the steps to use the syslog-receiver utility:

1. Open a terminal or command prompt.
2. Navigate to the Delve directory.
3. Execute `set-env.bat` (Windows) or `source set-env` (Linux/Mac).
4. Execute `python utilities/cli/syslog-receiver.py --help`.
5. Run the script with the appropriate arguments.

### Command-line Arguments
The `syslog-receiver.py` script accepts the following command-line arguments:

- `--server`: The scheme, host, and port of the Delve server (default: `http://localhost:8000`).
- `--no-verify`: If specified, TLS hostname verification will be disabled.
- `-i, --index`: The index in which to store the event (default: `default`).
- `-H, --host`: The host to associate with the event (default: the IP address of the client).
- `-s, --source`: The source to associate with the event (default: `text/syslog`).
- `-t, --sourcetype`: The sourcetype to associate with the event (default: `text/syslog`).
- `-u, --username`: The username to use for authentication (if omitted, you will be prompted).
- `-p, --password`: The password to use for authentication (if omitted, you will be prompted).
- `--line-ending`: The type of line endings to expect (`linux`, `macos`, `windows`).
- `--udp`: If specified, will listen for UDP messages.
- `--tcp`: If specified, will listen for TCP messages.
- `--tcp-port`: The TCP port to listen on (default: `1514`).
- `--tcp-cert`: If this and `--tcp-key` are specified, the TCP listener will use TLS.
- `--tcp-key`: If this and `--tcp-cert` are specified, the TCP listener will use TLS.
- `--udp-port`: The UDP port to listen on (default: `2514`).
- `--hostname`: The hostname (or IP) to listen on.
- `-v, --verbose`: Increase verbosity of log output.
- `-l, --log-file`: The file to which logs will be written (default: `log/syslog-receiver-<pid>.log`).
- `--batch-size`: The number of events to send to the Delve server per request (default: `10000`).
- `--max-queue-size`: The maximum number of events waiting to be uploaded to Delve (default: `10000`).

### Example Usage
Here are some example commands to use the syslog-receiver utility:

```bash
# Basic usage with default settings for UDP
python utilities/cli/syslog-receiver.py --udp

# Basic usage with default settings for TCP
python utilities/cli/syslog-receiver.py --tcp

# Basic usage with default settings for TCP and UDP
python utilities/cli/syslog-receiver.py --tcp --udp

# Listen on a custom port for TCP
python utilities/cli/syslog-receiver.py --tcp --tcp-port 9514

# Specify a custom index and sourcetype for UDP
python utilities/cli/syslog-receiver.py --udp --index "my_index" --sourcetype "my_sourcetype"

# Specify a custom index and sourcetype for TCP
python utilities/cli/syslog-receiver.py --tcp --index "my_index" --sourcetype "my_sourcetype"

# Use TLS for TCP with specified certificate and key
python utilities/cli/syslog-receiver.py --tcp --tcp-cert "/path/to/cert.pem" --tcp-key "/path/to/key.pem"

# Disable TLS hostname verification for the Delve server
python utilities/cli/syslog-receiver.py --no-verify --server "https://delve.example.com" --tcp

# Provide username and password for authentication to prevent being prompted
python utilities/cli/syslog-receiver.py --username "myuser" --password "mypassword" --udp

# Lowest verbosity of log output (less than default)
python utilities/cli/syslog-receiver.py -v --udp

# Most verbose log output (more than default)
python utilities/cli/syslog-receiver.py -vvvvvv --udp
```

### Additional Information
The syslog-receiver utility supports both UDP and TCP for receiving syslog messages. You can specify the supported protocols using the `--udp` or `--tcp` arguments. If you want to use TLS for TCP, you need to provide the certificate and key files using the `--tcp-cert` and `--tcp-key` arguments.

The utility batches events to improve performance. You can configure the batch size and the maximum queue size using the `--batch-size` and `--max-queue-size` arguments, respectively.

## Upload a File Directly
Delve allows direct file uploads for data ingestion, facilitating one-time or batch data imports from various file formats. The upload interface enables users to select and upload files, which are subsequently processed and ingested into the platform.

### Methods of Upload
Files can be uploaded using the following methods:

- **REST API**: Perform a POST request to `/api/files/` with the file included as a multipart/form-encoded payload.
- **Explore UI**: Click the "File Uploads" button at the top of the page to reveal the file upload form.
- **Admin UI**: Click "File Uploads" on the left-hand side.

### Reading Uploaded Files
Once a file is uploaded, it can be read into a search using the `read_file` command. For example, if a file is named "example.xml", it can be read into a search with the following command:

```bash
read_file example.xml
```

By default, `read_file` returns the contents of the file in the `content` field as an array of lines. To parse the XML, use the following command:

```bash
read_file --parse xml example.xml
```

### Parse Options
The following parse options are currently available:

- `csv`
- `json`
- `jsonl`
- `xml`

## Through Searches (Interactive and Scheduled)
Delve supports both interactive and scheduled searches, allowing users to define search queries that retrieve data from external sources and import it into Delve on a regular basis or on-demand.

### Search Commands
Delve provides several built-in search commands to retrieve, parse, and transform data. Some of the key search commands include:

- `search`: Retrieve data through Delve, including the models of registered apps.
- `request`: Perform an HTTP request and return the data.
- `read_file`: Retrieve data from an uploaded file.

Custom search commands can also be defined to retrieve, parse, and/or transform data.

Check the [Search Command Reference](Search_Command_Reference.md) for a list of all search commands included with Delve.

Custom or third-party Delve apps can also define search commands, but all search commands must be configured in `settings.py` under `DELVE_SEARCH_COMMANDS` in order to be used.

### Example Usage
Here are some example commands to use the search functionality:

```bash
# Basic search to retrieve data from the delve database  
search --index default text__icontains="error"

# Perform an HTTP request and return the data
request GET https://api.example.com/data

# Retrieve data from an uploaded file
read_file example.xml
```

### make_events Command
The `make_events` command allows you to generate events based on the current result set and index them into the Delve database. This command is useful for creating new events from existing data or external sources gathered with other search commands like `request`.

#### Command-line Arguments
The `make_events` command accepts the following command-line arguments:

- `-i, --index`: The index to assign to the new events. You can use dollar sign notation to assign the value of a field.
- `-o, --host`: The host to assign to the new events. You can use dollar sign notation to assign the value of a field.
- `-s, --source`: The source to assign to the new events. You can use dollar sign notation to assign the value of a field.
- `-t, --sourcetype`: The sourcetype to assign to the new events. You can use dollar sign notation to assign the value of a field.
- `-S, --save`: If specified, the events will be saved.
- `-d, --drop`: If specified, provide the name of a field to drop before creating the events.

#### Example Usage
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

---

[Previous: Configuration](Using_the_Web_UI.md) | [Next: User and Group Management](User_and_Group_Management.md)
