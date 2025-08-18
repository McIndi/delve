# Backup and Restore

Performing regular backups is essential to prevent data loss and ensure data integrity. This section covers how to back up and restore your Delve instance using Django's `dumpdata` and `loaddata` commands.

## Backing Up Data
Use the `dumpdata` command to export data from the database to a JSON file. This command can be used to back up specific apps or the entire database.

### Backing Up the Entire Database
To back up the entire database, run the following command:

```bash
fl dumpdata > backup.json
```

### Backing Up Specific Apps
To back up specific apps (e.g., `users`, `auth`), run the following command:

```bash
fl dumpdata users auth > backup_users_auth.json
```

### Scheduling Backups
You can schedule regular backups using a task scheduler like `cron` on Linux or Task Scheduler on Windows. Here is an example of a `cron` job that runs a backup every day at midnight:

```cron
0 0 * * * /path/to/delve/venv/bin/fl dumpdata > /path/to/backups/backup_$(date +\%F).json
```

## Restoring Data
Use the `loaddata` command to import data from a JSON file into the database. This command can be used to restore data from a backup.

### Restoring Data from a Backup File
To restore data from a backup file, run the following command:

```bash
fl loaddata backup.json
```

The `loaddata` command will load the data into the proper app automatically.

## Custom User Model
Delve includes a custom user model in the `users` app. However, the default Django `Group` and `Permission` models are used for managing user roles and permissions. When performing backups and restores, ensure that data from the `users` app and the `auth` app is included to maintain user accounts and permissions.

## Automating Backups and Restores
Automating backups and restores can help ensure that your data is always protected and can be quickly restored in case of an issue. Here are some tips for automating these processes:

### Automating Backups
1. **Create a Backup Script**: Create a script that runs the `dumpdata` command and saves the output to a file.
2. **Schedule the Script**: Use a task scheduler like `cron` on Linux or Task Scheduler on Windows to run the script at regular intervals.

### Example Backup Script
Here is an example backup script for Linux:

```bash
#!/bin/bash

# Set the path to the Delve directory
DELVE_DIR="/path/to/delve"

# Run the backup command
$DELVE_DIR/fl dumpdata > "$DELVE_DIR/backups/backup_$(date +\%F).json"
```

### Automating Restores
1. **Create a Restore Script**: Create a script that runs the `loaddata` command and restores data from a backup file.
2. **Schedule the Script**: Use a task scheduler like `cron` on Linux or Task Scheduler on Windows to run the script as needed.

### Example Restore Script
Here is an example restore script for Linux:

```bash
#!/bin/bash

# Set the path to the Delve directory
DELVE_DIR="/path/to/delve"

# Run the restore command
$DELVE_DIR/fl loaddata "$DELVE_DIR/backups/backup.json"
```

By following these steps, you can effectively back up and restore your Delve instance, ensuring that your data is protected and can be quickly recovered in case of an issue.

---

[Previous: Performance Tuning](Performance_Tuning.md) | [Next: Scaling and Load Balancing](Scaling_and_Load_Balancing.md)
