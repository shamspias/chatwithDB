import psycopg2
import mysql.connector
from pymongo import MongoClient


class QueryView:
    """
    Maintain Database connection and similarity Search
    """

    @staticmethod
    def get_text_fields_postgres(cur, table_name):
        # Specific for PostgreSQL
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s AND data_type = 'text'",
                    (table_name,))
        return [row[0] for row in cur.fetchall()]

    @staticmethod
    def get_text_fields_mysql(cur, table_name):
        # Specific for MySQL, you might need to adjust the query
        cur.execute(f"SHOW COLUMNS FROM {table_name} WHERE type LIKE '%%text%%'")
        return [row[0] for row in cur.fetchall()]

    @staticmethod
    def find_similar_data(db_config, message):
        # Choose the right database connector and text field retrieval method based on db type
        if db_config.type == 'POSTGRESQL':
            conn = psycopg2.connect(database=db_config.name, user=db_config.username, password=db_config.password,
                                    host=db_config.host, port=db_config.port)
            cur = conn.cursor()
            get_text_fields = QueryView.get_text_fields_postgres
            # PostgreSQL specific SQL command to list tables
            cur.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        elif db_config.type == 'MYSQL':
            conn = mysql.connector.connect(user=db_config.username, password=db_config.password, host=db_config.host,
                                           database=db_config.name)
            cur = conn.cursor()
            get_text_fields = QueryView.get_text_fields_mysql
            # MySQL specific SQL command to list tables
            cur.execute("""SHOW TABLES""")

        elif db_config.type == 'MONGODB':
            client = MongoClient(host=db_config.host, port=db_config.port)
            db = client[db_config.name]

            results = []

            # Iterate over all collections
            for collection_name in db.list_collection_names():
                collection = db[collection_name]

                # MongoDB regex search
                for doc in collection.find({"$or": [{"$regex": message} for _ in doc]}):
                    # Append the entire document to the results
                    # Modify this if you only want to append specific fields
                    results.append(doc)

            return results

        else:
            # Add other database types if needed
            return []

        tables = cur.fetchall()

        results = []

        # Iterate over all tables and their text fields
        for table in tables:
            table_name = table[0]
            text_fields = get_text_fields(cur, table_name)

            for field in text_fields:
                if db_config.type == 'POSTGRESQL':

                    # PostgreSQL specific similarity search
                    cur.execute(
                        f"SELECT {field} FROM {table_name} WHERE {field} ILIKE %s",
                        (f"%{message}%",))
                elif db_config.type == 'MYSQL':
                    # MySQL does not support `similarity` but you can use `LIKE` as a basic approximation
                    cur.execute(f"SELECT {field} FROM {table_name} WHERE {field} LIKE %s", (f"%{message}%",))

                # Fetch the results
                results += cur.fetchall()

        # Format the results
        similar_data = ', '.join([str(result[0]) for result in results])

        return similar_data
