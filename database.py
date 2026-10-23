import os

import mysql.connector

class database:
    HOST = ""
    USER = ""
    PASSWORD = os.environ.get("MYSQL_PASSWORD")
    DB_NAME = ""
    PORT = 3306

class RecordDAO:
    def __init__(self):
        if not database.PASSWORD:
            raise RuntimeError("Define la variable de entorno MYSQL_PASSWORD antes de iniciar la aplicación.")

        self.conn = mysql.connector.connect(
            host=database.HOST,
            user=database.USER,
            password=database.PASSWORD,
            port=database.PORT
        )
        self.create_database_and_table()

    def create_database_and_table(self):
        cursor = self.conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database.DB_NAME}")
        cursor.execute(f"USE {database.DB_NAME}")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Discos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                artist VARCHAR(150) NOT NULL,
                album VARCHAR(150) NOT NULL,
                format VARCHAR(50) NOT NULL,
                genre VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                stock INT NOT NULL,
                cover_path VARCHAR(255)
            )
        ''')
        self.conn.commit()
        cursor.close()

    def insert_record(self, artist, album, format_type, genre, price, stock, cover_path):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Discos (artist, album, format, genre, price, stock, cover_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (artist, album, format_type, genre, price, stock, cover_path))
        self.conn.commit()
        cursor.close()

    def update_record(self, record_id, artist, album, format_type, genre, price, stock, cover_path):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE Discos
            SET artist=%s, album=%s, format=%s, genre=%s, price=%s, stock=%s, cover_path=%s
            WHERE id=%s
        ''', (artist, album, format_type, genre, price, stock, cover_path, record_id))
        self.conn.commit()
        cursor.close()

    def update_stock(self, record_id, new_stock):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE Discos SET stock=%s WHERE id=%s', (new_stock, record_id))
        self.conn.commit()
        cursor.close()

    def get_all_records(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Discos')
        records = cursor.fetchall()
        cursor.close()
        return records

    def delete_record(self, record_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM Discos WHERE id = %s', (record_id,))
        self.conn.commit()
        cursor.close()

    def close_connection(self):
        self.conn.close()