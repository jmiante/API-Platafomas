import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from local_settings import host, port, user, password, database

import mysql.connector
import pandas as pd



def tab():
    return print(f"{'-'*50}\n")   


class Database:
    host=host
    port=port
    user=user
    password=password
    database=database

    def __init__(self): 
        self.columns_numbers = []

    def save_sql(self, sql):
        conn = mysql.connector.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.database)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def connect(self):
        return mysql.connector.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.database)

    def read_sql(self, sql):
        conn = mysql.connector.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.database)
        df = pd.read_sql(sql, conn)
        conn.close()
        for c in self.columns_numbers:
            df[c] = df[c].map(lambda x: f"{x:,.2f}".replace('.', '||').replace(',', '.').replace('||', ','))

        return df