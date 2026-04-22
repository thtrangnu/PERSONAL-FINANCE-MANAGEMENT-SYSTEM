from mysql.connector.django.base import DatabaseWrapper as MySQLConnectorDatabaseWrapper


class DatabaseWrapper(MySQLConnectorDatabaseWrapper):
    display_name = 'MySQL'

