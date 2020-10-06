from google.cloud import spanner

from google.cloud.spanner_dbapi import connection


def create_connection(instance_id, database_id):
    # Instantiate a client.
    spanner_client = spanner.Client()

    # Get a Cloud Spanner instance by ID.
    instance = spanner_client.instance(instance_id)

    # Get a Cloud Spanner database by ID.
    database = instance.database(database_id)

    # Creating connection in linked Database.
    my_connection = connection.Connection(database)
    print("Connection is created.")


if __name__ == "__main__":
    create_connection("my-instance-id", "my-database-id")
