# Getting Started

## Overview
Delve is a versatile and powerful platform for ingesting, transforming, and searching through structured, unstructured, and semi-structured data. It allows for interactive searches, dashboards, alerts, and more.

## Key Features
- Ingest data from various sources
- Transform and normalize data
- Powerful search capabilities
- Interactive dashboards and visualizations
- Alerts and notifications
- Extensible and customizable

## Use Cases
- Log analysis and monitoring
- Data exploration and visualization
- Real-time alerting and notifications
- API data crawling and analysis
- Troubleshooting and debugging

## Project Goals
- Provide a user-friendly interface for data exploration
- Enable quick and efficient data ingestion and transformation
- Offer powerful search and filtering capabilities
- Support interactive and customizable dashboards
- Facilitate real-time alerting and notifications

## Basic Concepts
Delve is built around several core concepts that enable its powerful functionality:

### Events
Events are the basic unit of data in Delve. They are stored in a database and consist of indexed fields such as `created`, `index`, `source`, and `host`. Additionally, events contain a JSON field called `extracted_fields` for storing information extracted from the event.

Events can be created through the Delve REST API or via queries using search commands, either interactively or on a scheduled basis.

### Queries
Queries are used to retrieve, transform, and store data. They can be ephemeral or persisted in the database. A query's `text` field defines the pipeline through which events are processed using search commands.

Queries use a pipeline syntax where commands are chained together with the `|` operator, similar to command-line shells. For example:

```bash
search --last-15-minutes index=default
| select extracted_fields
| explode extracted_fields
```

This query retrieves events from the last 15 minutes, selects specific fields, and expands key-value pairs into individual fields.

### Ingestion
Ingestion is the process of importing data into Delve. This can be done through various methods:
- **REST API**: Programmatically send data to Delve.
- **File-tail Utility**: Monitor and stream log files in real-time.
- **Syslog**: Collect logs from network devices and servers via UDP, TCP, or TLS.
- **Searches**: Use interactive or scheduled queries to ingest data.

### Field Extraction and Preprocessing
Field extraction identifies and extracts specific fields from data. Delve supports:
- **Index-time Extractions**: Applied during data ingestion and persisted in the database.
- **Search-time Extractions**: Dynamically extract fields during a search (can be persisted to the database or ephemeral).
- **Preprocessing**: Take action (email, log, etc.) on certain events during ingestion.

### Search
Search functionality allows querying and filtering data, as well as performing transformations, visualizations, and more. Delve supports custom search commands written in Python, which can be registered in the configuration.

### Custom Apps
Delve enables the creation of custom apps to group related data and code. These apps can include custom search commands, dashboards, REST API endpoints, and more.

### Alerts
Delve provides search-based and processor-based alerts:
- **Search-based Alerts**: Triggered by saved queries and scheduled tasks.
- **Processor-based Alerts**: Triggered during data ingestion based on event sourcetype.

## Installation
For installation instructions, please refer to the [Delve Administration Manual](../administration/index.md). The User Manual assumes that Delve is already installed and configured.

## Logging In
Once Delve is installed, you can log in to the web interface using the credentials provided by your administrator.

## User Interface Overview
The Delve web interface consists of several key components:

- **Browsable REST API**: Provides access to almost all of the data that Delve has.
- **Documentation**: Comprehensive documentation for using and configuring Delve.
- **Explore UI**: A dynamic, universal search interface.
- **Admin UI**: An administrative dashboard for managing users, data sources, and system settings.

[Previous: Index](../administration/index.md) | [Next: Installation and Setup](../administration/Installation_and_Setup.md)
