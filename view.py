def show_message(akcia, rowcount):
    spravy = {
        "add":    ("zaznam bol pridany", "zaznam sa nepodarilo pridat"),
        "delete": ("zaznam bol vymazany", "zaznam s tymto ID neexistuje"),
        "update": ("zaznam bol aktualizovany", "zaznam s tymto ID neexistuje"),
        "borrow": ("kniha bola pozicana", "knihu sa nepodarilo vypozicat"),
        "return": ("kniha bola vratena", "vypozicka s tymto ID neexistuje"),
    }
    ok, fail = spravy[akcia]
    print(ok if rowcount else fail)

def show_results(typ, data):
    if not data:
        print("ziadne vysledky")
        return
    if typ == "books":
        for row in data:
            print(f"ID: {row[0]} | nazov: {row[1]} | autor: {row[8]} | zaner: {row[11]} | isbn: {row[4]} | rok: {row[5]} | pocet kopii: {row[6]}")
    elif typ == "members":
        for row in data:
            print(f"ID: {row[0]} | meno: {row[1]} {row[2]} | email: {row[3]} | registracia: {row[4]}")
    elif typ == "loans":
        for row in data:
            status = "vratena" if row[4] else "vypozicana"
            print(f"ID: {row[0]} | kniha: {row[1]} | vypozicana: {row[2]} | termin: {row[3]} | status: {status}")
