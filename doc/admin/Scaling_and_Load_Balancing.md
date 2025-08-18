# Scaling and Load Balancing

Scaling and load balancing are essential for ensuring that your Delve instance can handle increased load and provide high availability. This section covers scaling and load balancing for the database, web app, and task scheduler.

## Database Scaling and Load Balancing
Delve supports any database supported by Django ORM, including SQLite, PostgreSQL, MySQL, and others. The scaling and load balancing strategies depend on the database in use.

### PostgreSQL
PostgreSQL is a powerful, open-source relational database that supports various scaling and load balancing techniques.

#### Scaling
- **Vertical Scaling**: Increase the resources (CPU, memory, storage) of the database server.
- **Horizontal Scaling**: Use replication to create read replicas for distributing read queries.

#### Load Balancing
- **PgBouncer**: A lightweight connection pooler for PostgreSQL.
- **HAProxy**: A high-availability load balancer that can distribute database connections across multiple servers.

### MySQL
MySQL is another popular relational database that supports various scaling and load balancing techniques.

#### Scaling
- **Vertical Scaling**: Increase the resources (CPU, memory, storage) of the database server.
- **Horizontal Scaling**: Use replication to create read replicas for distributing read queries.

#### Load Balancing
- **ProxySQL**: A high-performance proxy for MySQL.
- **HAProxy**: A high-availability load balancer that can distribute database connections across multiple servers.

## Web App Scaling and Load Balancing
The Delve web app is a WSGI application and uses CherryPy as the built-in production web server. For load balancing, you can run multiple instances of the web app and use a load balancer to distribute traffic.

### Scaling
- **Vertical Scaling**: Increase the resources (CPU, memory) of the web server.
- **Horizontal Scaling**: Run multiple instances of the web app and distribute traffic using a load balancer.

### Load Balancing
- **Nginx**: A high-performance web server and reverse proxy that can load balance HTTP traffic.
- **HAProxy**: A high-availability load balancer that can distribute HTTP traffic across multiple web servers.
- **AWS Elastic Load Balancing (ELB)**: A managed load balancing service provided by AWS.

## Task Scheduler Scaling
Delve uses Django Q as the task scheduler, which supports various scaling options.

### Scaling
- **Vertical Scaling**: Increase the resources (CPU, memory) of the task scheduler server.
- **Horizontal Scaling**: Run multiple instances of the task scheduler to distribute the task load.

### Configuring Django Q with Redis
Using Redis as a backend for Django Q can improve performance and scalability compared to using the Django ORM.

#### Install Redis and Django Q Redis dependencies
```bash
pip install django-q[redis]
```

#### Configure Django Q to use Redis in `settings.py`
```python
# filepath: /delve/settings.py
Q_CLUSTER = {
    'name': 'delve',
    'workers': 4,  # Number of worker processes
    'recycle': 500,
    'timeout': 60,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',  # Change this to 'redis' to use Redis as the backend
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': 'your_redis_password',  # Optional
        'socket_timeout': None,
        'charset': 'utf-8',
        'errors': 'strict',
        'max_connections': None,
        'unix_socket_path': None
    }
}
```

#### Start the Redis server
Ensure that the Redis server is running. You can start it using the following command:
```bash
redis-server
```

### Other Backend Options
In addition to Redis, Django Q supports other backends such as IronMQ, SQS, and MongoDB. Here is an example configuration for each:

#### IronMQ
```python
# filepath: /delve/settings.py
Q_CLUSTER = {
    'name': 'delve',
    'workers': 4,
    'recycle': 500,
    'timeout': 60,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
    'iron': {
        'token': 'your_ironmq_token',
        'project_id': 'your_ironmq_project_id',
        'queue': 'your_queue_name'
    }
}
```

#### SQS (Amazon Simple Queue Service)
```python
# filepath: /delve/settings.py
Q_CLUSTER = {
    'name': 'delve',
    'workers': 4,
    'recycle': 500,
    'timeout': 60,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
    'sqs': {
        'aws_access_key_id': 'your_aws_access_key_id',
        'aws_secret_access_key': 'your_aws_secret_access_key',
        'region_name': 'your_aws_region',
        'queue_name': 'your_queue_name'
    }
}
```

#### MongoDB
```python
# filepath: /delve/settings.py
Q_CLUSTER = {
    'name': 'delve',
    'workers': 4,
    'recycle': 500,
    'timeout': 60,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
    'mongo': {
        'host': 'localhost',
        'port': 27017,
        'database': 'django_q',
        'collection': 'tasks',
        'username': 'your_mongo_username',
        'password': 'your_mongo_password',
        'authSource': 'admin'
    }
}
```

## Ports Used by Delve
Delve uses several ports for different services. Here is a list of ports used by Delve and other common ports that might be relevant depending on the use case:

- **Delve Web UI**: Default port 8000 (configurable in `settings.py` with `DELVE_SERVER_PORT`)
- **Django Q Task Scheduler**: No specific port, runs as a background process
- **Syslog (UDP)**: Default port 514 (configurable in `syslog-receiver.py` with `--udp-port`)
- **Syslog (TCP)**: Default port 1514 (configurable in `syslog-receiver.py` with `--tcp-port`)
- **PostgreSQL**: Default port 5432
- **MySQL**: Default port 3306
- **PgBouncer**: Default port 6432
- **ProxySQL**: Default port 6033
- **Nginx**: Default port 80 (HTTP) and 443 (HTTPS)
- **HAProxy**: Configurable, commonly uses ports 80 (HTTP) and 443 (HTTPS)

By following these scaling and load balancing strategies, you can ensure that your Delve instance can handle increased load and provide high availability.

---

[Previous: Backup and Restore](Backup_and_Restore.md) | [Next: Advanced Logging](Advanced_Logging.md)
