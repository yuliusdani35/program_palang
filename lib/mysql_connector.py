import mysql.connector
from mysql.connector import pooling, Error

class MySQLConnectionPool:
    def __init__(self, pool_name, pool_size, host, port, database, user, password):
        self.pool_name = pool_name
        self.pool_size = pool_size
        self.pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=self.pool_name,
            pool_size=self.pool_size,
            pool_reset_session=True,
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

    def get_connection(self):
        try:
            connection = self.pool.get_connection()
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error: {e}")
            return None

def execute_query(pool, query, params=None):
    connection = pool.get_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            connection.commit()
            return cursor
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

def fetch_all(pool, query, params=None):
    connection = pool.get_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

def fetch_one(pool, query, params=None):
    connection = pool.get_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

class AttendanceDB:
    def __init__(self, pool):
        self.pool = pool
        self.create_table()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            date DATE NOT NULL,
            hours_in TIME NOT NULL,
            hours_out TIME NOT NULL,
            predict_time INT NOT NULL DEFAULT 0,
            path VARCHAR(255) NOT NULL DEFAULT ''
        );
        """
        execute_query(self.pool, create_table_query)

    def insert_data(self, data):
        insert_query = """
        INSERT INTO attendance (name, date, hours_in, hours_out, predict_time, path)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        execute_query(self.pool, insert_query, data)

    def update_hours_in(self, data):
        update_query = """
        UPDATE attendance SET hours_in = %s, predict_time = %s, path = %s WHERE name = %s AND date = %s;
        """
        execute_query(self.pool, update_query, data)

    def update_hours_out(self, data):
        update_query = """
        UPDATE attendance SET hours_out = %s, predict_time = %s, path = %s WHERE name = %s AND date = %s;
        """
        execute_query(self.pool, update_query, data)

    def read_data(self):
        read_query = "SELECT * FROM attendance;"
        return fetch_all(self.pool, read_query)

    def update_data(self, id, predict_time=None, path=None):
        update_query = "UPDATE attendance SET "
        updates = []
        values = []
        if predict_time is not None:
            updates.append("predict_time = %s")
            values.append(predict_time)
        if path is not None:
            updates.append("path = %s")
            values.append(path)
        update_query += ", ".join(updates) + " WHERE id = %s;"
        values.append(id)
        execute_query(self.pool, update_query, tuple(values))

    def delete_data(self, id):
        delete_query = "DELETE FROM attendance WHERE id = %s;"
        execute_query(self.pool, delete_query, (id,))