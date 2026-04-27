class Loan:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

    def borrow(self, book_id, member_id, due_date):
        try:
            self.cursor.execute("""
                UPDATE books SET copies = copies - 1 WHERE book_id = %s AND copies > 0
            """, (book_id,))
            updated = self.cursor.rowcount
            if updated == 0:
                self.conn.rollback()
                return False
            self.cursor.execute("""
                INSERT INTO loans (book_id, member_id, due_date)
                VALUES (%s, %s, %s)
            """, (book_id, member_id, due_date))
            inserted = self.cursor.rowcount
            self.conn.commit()
            return inserted
        except Exception:
            self.conn.rollback()
            return False

    def return_book(self, loan_id):
        try:
            self.cursor.execute("""
                UPDATE loans SET return_date = CURRENT_DATE WHERE loan_id = %s AND return_date IS NULL
            """, (loan_id,))
            if self.cursor.rowcount == 0:
                self.conn.rollback()
                return False
            self.cursor.execute("""
                UPDATE books SET copies = copies + 1
                WHERE book_id = (SELECT book_id FROM loans WHERE loan_id = %s)
            """, (loan_id,))
            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            return False

    def search(self, member_id):
        self.cursor.execute("""
            SELECT l.loan_id, b.title, l.loan_date, l.due_date, l.return_date
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            WHERE l.member_id = %s
            ORDER BY l.loan_date DESC
        """, (member_id,))
        return self.cursor.fetchall()
