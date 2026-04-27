class Book:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

    def add(self, title, author_id, genre_id, isbn, publication_year, copies):
        self.cursor.execute("""
            INSERT INTO books (title, author_id, genre_id, isbn, publication_year, copies)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, author_id, genre_id, isbn, publication_year, copies))
        self.conn.commit()
        return self.cursor.rowcount

    def delete(self, book_id):
        self.cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
        self.conn.commit()
        return self.cursor.rowcount

    def search(self, kluc):
        self.cursor.execute("""
            SELECT * FROM books b
            JOIN authors a ON b.author_id = a.author_id
            LEFT JOIN genres g ON b.genre_id = g.genre_id
            WHERE b.title ILIKE %s
            OR a.name ILIKE %s
            OR g.name ILIKE %s
        """, (f"%{kluc}%", f"%{kluc}%", f"%{kluc}%"))
        return self.cursor.fetchall()
        # if results:
        #     for riadok in results:
        #         print(riadok)
        # else:
        #     print("kniha nebola najdena")

    def update(self, book_id, title=None, author_id=None, genre_id=None, isbn=None, publication_year=None, copies=None):
        fields = []
        values = []
        data = {
            "title": title,
            "author_id": author_id,
            "genre_id": genre_id,
            "isbn": isbn,
            "publication_year": publication_year,
            "copies": copies
        }
        for key, value in data.items():
            if value is not None:
                fields.append(f"{key} = %s")
                values.append(value)
        if not fields:
            return 0
        values.append(book_id)
        query = "UPDATE books SET " + ', '.join(fields) + " WHERE book_id = %s"
        self.cursor.execute(query, tuple(values))
        updated = self.cursor.rowcount
        self.conn.commit()
        return updated
