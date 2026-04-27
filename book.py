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
        print(f"kniha {title} bola pridana do zoznamu")

    def delete(self, book_id):
        self.cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
        self.conn.commit()

    def search(self, kluc):
        self.cursor.execute("""
            SELECT * FROM books b
            JOIN authors a ON b.author_id = a.author_id
            LEFT JOIN genres g ON b.genre_id = g.genre_id
            WHERE b.title ILIKE %s
            OR a.name ILIKE %s
            OR g.name ILIKE %s
        """, (f"%{kluc}%", f"%{kluc}%", f"%{kluc}%"))
        results = self.cursor.fetchall()
        if results:
            for riadok in results:
                print(riadok)
        else:
            print("kniha nebola najdena")

    def update(self, book_id, title=None, author_id=None, genre_id=None, isbn=None, publication_year=None, copies=None):
        fields = []
        values = []
        if title:
            fields.append("title = %s")
            values.append(title)
        if author_id is not None:
            fields.append("author_id = %s")
            values.append(author_id)
        if genre_id is not None:
            fields.append("genre_id = %s")
            values.append(genre_id)
        if isbn:
            fields.append("isbn = %s")
            values.append(isbn)
        if publication_year is not None:
            fields.append("publication_year = %s")
            values.append(publication_year)
        if copies is not None:
            fields.append("copies = %s")
            values.append(copies)
        if not fields:
            print("ziadne udaje na aktualizaciu")
            return
        values.append(book_id)
        query = "UPDATE books SET " + ', '.join(fields) + " WHERE book_id = %s"
        self.cursor.execute(query, tuple(values))
        self.conn.commit()
        print(f"kniha s id {book_id} bola aktualizovana")
