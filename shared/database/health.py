from shared.database.mysql import get_mysql_connection
from shared.database.mongodb import get_mongo_client


def mysql_health_check():

    connection = get_mysql_connection()

    return connection.open


def mongodb_health_check():

    client = get_mongo_client()

    return client.admin.command("ping")