from dotenv import load_dotenv
import os, psycopg2
from book import Book
from members import Member
from loans import Loan
from view import show_results, show_message

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

# cursor.execute("UPDATE loans SET return_date = CURRENT_TIMESTAMP WHERE return_date IS NULL")
# conn.commit()

try:
    while True:
        print("1 knihy")
        print("2 clenovia")
        print("3 vypozicky")
        print("0 Koniec")
        volba = input("volba: ")
        if volba == "1":
            print("\n1 pridat knihu")
            print("2 vymazat knihu")
            print("3 vyhľadat knihu")
            print("4 aktualizovat knihu")
            akcia = input("volba: ")
            if akcia == "1":
                title = input("nazov: ")
                author_id = int(input("ID autora: "))
                genre_id = int(input("ID zanru: "))
                isbn = input("isbn: ")
                year = int(input("rok vydania: "))
                copies = int(input("počet kopii: "))
                result = book.add(title, author_id, genre_id, isbn, year, copies)
                show_message("add", result)
            elif akcia == "2":
                book_id = int(input("ID knihy: "))
                result = book.delete(book_id)
                show_message("delete", result)
            elif akcia == "3":
                kluc = input("hladat: ")
                results = book.search(kluc)
                show_results("books", results)
            elif akcia == "4":
                book_id = int(input("ID knihy: "))
                title = input("novy nazov (enter = preskocit): ") or None
                copies = input("novy pocet kopii (enter = preskocit): ")
                copies = int(copies) if copies else None
                result = book.update(book_id, title=title, copies=copies)
                show_message("update", result)
        elif volba == "2":
            print("\n1 registrovat clena")
            print("2 vymazat clena")
            print("3 vyhladat clena")
            akcia = input("volba: ")
            if akcia == "1":
                first_name = input("meno: ")
                last_name = input("priezvisko: ")
                email = input("email: ")
                result = member.add(first_name, last_name, email)
                show_message("add", result)
            elif akcia == "2":
                member_id = int(input("ID clena: "))
                result = member.delete(member_id)
                show_message("delete", result)
            elif akcia == "3":
                kluc = input("hladat: ")
                results = member.search(kluc)
                show_results("members", results)
        elif volba == "3":
            print("\n1 pozicat knihu")
            print("2 vratit knihu")
            print("3 historia vypoziciek")
            akcia = input("volba: ")
            if akcia == "1":
                book_id = int(input("ID knihy: "))
                member_id = int(input("ID clena: "))
                due_date = input("termin vratenia (pozor! len vo formate YYYY-MM-DD): ")
                result = loan.borrow(book_id, member_id, due_date)
                show_message("borrow", result)
            elif akcia == "2":
                loan_id = int(input("ID vypozicky: "))
                result = loan.return_book(loan_id)
                show_message("return", result)
            elif akcia == "3":
                member_id = int(input("ID clena: "))
                results = loan.search(member_id)
                show_results("loans", results)
        elif volba == "0":
            break

finally:
    cursor.close()
    conn.close()

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

# results = loan.search(3)
# print(results)

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
