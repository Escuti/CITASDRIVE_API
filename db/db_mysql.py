import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

MYSQL_USER= os.environ["MYSQL_USER"]
MYSQL_PASSWORD= os.environ["MYSQL_PASSWORD"]
MYSQL_HOST= os.environ["MYSQL_HOST"]
MYSQL_PORT= os.environ["MYSQL_PORT"]
MYSQL_DATABASE= os.environ["MYSQL_DATABASE"]

class CoonectDB:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        '''Establecemos la conexión a la BD'''
        if not self.connection or not self.connection.open:
            try:
                self.connection = pymysql.connect(
                    host=MYSQL_HOST,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DATABASE,
                    port=int(MYSQL_PORT)
                )
                print("Conexión Exitosa")
            except Exception as e:
                print(f"Error al Conectar: {e}")
        return self.connection

    def disconnect(self):
        '''Cerrar conexión si está activa'''
        if self.connection or self.connection.open:
            self.connection.close()
            print("Conexión cerrada")

db_conn=CoonectDB()

def get_db_connection():
    return db_conn.connect()