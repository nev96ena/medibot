import psycopg2
from psycopg2 import sql

db_config = {
                            "host": "localhost",     
                            "port": 5432,             
                            "database": "mydb", 
                            "user": "nevenar",         
                            "password": "nevena123"
}
conn = psycopg2.connect(**db_config)

try:
    conn = psycopg2.connect(**db_config)
    print("Connected to the database!")

    cursor = conn.cursor()
    with open('mydb.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
        queries = sql_script.split(';')
        for query in queries:
            query = query.strip()
            if query:  
                try:
                    cursor.execute(query)
                except psycopg2.Error as e:
                    print(f"Error while executing query: {query}\nError: {e}")
                    conn.rollback() 
        conn.commit()


except psycopg2.Error as e:
    print(f"Error while executing SQL file: {e}")
    if conn:
        conn.rollback()
finally:
    if conn:
        cursor.close()
        conn.close()