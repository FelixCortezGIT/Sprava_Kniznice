class Loan:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

    def borrow(self, book_id, member_id, due_date):
        self.cursor.execute("""
            INSERT INTO loans (book_id, member_id, due_date)
            VALUES (%s, %s, %s)
        """, (book_id, member_id, due_date))
        self.cursor.execute("""
            UPDATE books SET copies = copies - 1 WHERE book_id = %s
        """, (book_id,))
        self.conn.commit()
        print("kniha bola vypozicana")

    def return_book(self, loan_id):
        self.cursor.execute("""
            UPDATE loans SET return_date = CURRENT_DATE WHERE loan_id = %s
        """, (loan_id,))
        self.cursor.execute("""
            UPDATE books SET copies = copies + 1
            WHERE book_id = (SELECT book_id FROM loans WHERE loan_id = %s)
        """, (loan_id,))
        self.conn.commit()
        print("kniha bola vratena")

    def search(self, member_id):
        self.cursor.execute("""
            SELECT l.loan_id, b.title, l.loan_date, l.due_date, l.return_date
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            WHERE l.member_id = %s
            ORDER BY l.loan_date DESC
        """, (member_id,))
        results = self.cursor.fetchall()
        if results:
            for riadok in results:
                print(riadok)
        else:
            print("clen nema vypozicky")
