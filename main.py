from dotenv import load_dotenv
import os, psycopg2

load_dotenv()
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

# with open("Query_1.sql", "r", encoding="utf-8") as file:
#     sql = file.read()
# cursor.execute(sql)
# conn.commit()

cursor.execute("SELECT * FROM books LIMIT 5")
books = cursor.fetchall()
for book in books:
    print(book)

cursor.close()
conn.close()
