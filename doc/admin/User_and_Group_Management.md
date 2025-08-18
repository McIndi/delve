# User and Group Management

Creating users and groups, as well as assigning permissions, is an essential part of managing your Delve instance. This section covers how to perform these tasks through the Django Admin Interface.

## Creating Admin Users from the Command Line

The following command can be used to create an Admin user from the command line:

```python
./fl createsuperuser
```

## Creating Users

To create a new user, follow these steps:

1. Log in to the Django Admin Interface using your admin credentials.
2. In the "Users" section, click "Add user".
3. Fill in the required fields, such as username, password, and email address.
4. Click "Save" to create the user.

## Creating Groups

To create a new group, follow these steps:

1. Log in to the Django Admin Interface using your admin credentials.
2. In the "Groups" section, click "Add group".
3. Enter a name for the group.
4. Select the permissions you want to assign to the group.
5. Click "Save" to create the group.

## Assigning Permissions

To assign permissions to a user or group, follow these steps:

1. Log in to the Django Admin Interface using your admin credentials.
2. Navigate to the "Users" or "Groups" section, depending on whether you want to assign permissions to a user or a group.
3. Click on the user or group you want to modify.
4. In the "Permissions" section, select the permissions you want to assign.
5. Click "Save" to apply the changes.

## Adding a User to a Group

To add a user to a group, follow these steps:

1. Log in to the Django Admin Interface using your admin credentials.
2. Navigate to the "Users" section and click on the user you want to add to a group.
3. In the "Groups" section, select the group(s) you want to add the user to.
4. Click "Save" to apply the changes.

By following these steps, you can effectively manage users, groups, and permissions in your Delve instance.

---

[Previous: Ingesting Data](Ingesting_Data.md.md) | [Next: Monitoring and Maintenance](Monitoring_and_Maintenance.md)
