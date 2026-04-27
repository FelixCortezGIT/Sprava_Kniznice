from dotenv import load_dotenv
import os, psycopg2
from book import Book
from members import Member
from loans import Loan

load_dotenv()
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()
book = Book(cursor, conn)
member = Member(cursor, conn)
loan = Loan(cursor, conn)

# book.search("Cesta bojovníka")
# # book.add("Slabikar", 1, 2, 9780000000099, 2026, 3)
# book.search("slabikar")
# book.update(106, title="Zahradkar", copies=5)
# book.search("slabikar")
# book.search("zahradkar")
# book.delete("106")
# book.search("zahradkar")

# member.search("Peter")
# # member.add("Tomas", "Macula", "test@email.com")
# member.search("macula")
# member.delete("44")
# member.search("macula")

results = loan.search(3)
print(results)

# loan.borrow(15, 3, "2026-05-27")
# loan.search(3)
# loan.return_book(96)
# loan.search(3)

# with open("Query_1.sql", "r", encoding="utf-8") as file:
#     sql = file.read()
# cursor.execute(sql)
# conn.commit()

# cursor.execute("SELECT * FROM books LIMIT 5")
# books = cursor.fetchall()
# for book in books:
#     print(book)

cursor.close()
conn.close()
