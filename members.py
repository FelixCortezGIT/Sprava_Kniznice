# REGISTRACIA CLENOV
# MAZANIE
# VYHLADAVANIE

class Member:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

    def add(self, first_name, last_name, email):
        self.cursor.execute("""
            INSERT INTO members (first_name, last_name, email)
            VALUES (%s, %s, %s)
        """, (first_name, last_name, email))
        self.conn.commit()
        print("novy clen zaregistrovany")

    def delete(self, member_id):
        self.cursor.execute("DELETE FROM members WHERE member_id = %s", (member_id,))
        self.conn.commit()

    def search(self, key):
        self.cursor.execute("""
            SELECT * FROM members
            WHERE first_name ILIKE %s
            OR last_name ILIKE %s
            OR email ILIKE %s
        """, (f"%{key}%", f"%{key}%", f"%{key}%"))
        results = self.cursor.fetchall()
        if results:
            for riadok in results:
                print(riadok)
        else:
            print("clen nenajdeny")
