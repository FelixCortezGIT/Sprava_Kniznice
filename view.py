import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
import os
import psycopg2
from book import Book
from members import Member
from loans import Loan

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


class AnimatedTabButton(tk.Frame):
    C_NORMAL   = "#2c3e50"
    C_HOVER    = "#3d5a73"
    C_SELECTED = "#2980b9"
    C_PRESS    = "#1f6391"
    C_TEXT     = "#ecf0f1"

    def __init__(self, parent, text, command, font_size=13, padx=20, pady=22):
        super().__init__(parent, bg=self.C_NORMAL, cursor="hand2")
        self._command = command
        self._selected = False
        self._fade_job = None

        self._label = tk.Label(
            self, text=text, bg=self.C_NORMAL, fg=self.C_TEXT,
            font=("Segoe UI", font_size, "bold"), padx=padx, pady=pady
        )
        self._label.pack(fill="both", expand=True)

        for w in (self, self._label):
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_press)
            w.bind("<ButtonRelease-1>", self._on_release)

    @staticmethod
    def _hex_to_rgb(c):
        c = c.lstrip("#")
        return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)

    @staticmethod
    def _rgb_to_hex(r, g, b):
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

    def _set_color(self, color):
        self.configure(bg=color)
        self._label.configure(bg=color)

    def _fade_to(self, to_c, steps=14):
        if self._fade_job:
            self.after_cancel(self._fade_job)
            self._fade_job = None
        from_c = self.cget("bg")
        r1, g1, b1 = self._hex_to_rgb(from_c)
        r2, g2, b2 = self._hex_to_rgb(to_c)

        def _step(s):
            if s > steps:
                return
            t = s / steps
            color = self._rgb_to_hex(
                r1 + (r2 - r1) * t,
                g1 + (g2 - g1) * t,
                b1 + (b2 - b1) * t
            )
            self._set_color(color)
            if s < steps:
                self._fade_job = self.after(16, _step, s + 1)

        _step(0)

    def _on_enter(self, _):
        if not self._selected:
            self._fade_to(self.C_HOVER)

    def _on_leave(self, _):
        if not self._selected:
            self._fade_to(self.C_NORMAL)

    def _on_press(self, _):
        self._set_color(self.C_PRESS)

    def _on_release(self, _):
        self._command()

    def select(self):
        self._selected = True
        self._fade_to(self.C_SELECTED)

    def deselect(self):
        self._selected = False
        self._fade_to(self.C_NORMAL)


class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sprava Kniznice")
        self.geometry("950x720")
        self.resizable(True, True)
        self.configure(bg="#1a252f")

        conn = get_connection()
        cursor = conn.cursor()
        self.book = Book(cursor, conn)
        self.member = Member(cursor, conn)
        self.loan = Loan(cursor, conn)

        self._build_nav()
        self._build_content()
        self._switch(0)

    # ------------------------------------------------------------------ MAIN NAV
    def _build_nav(self):
        nav = tk.Frame(self, bg="#1a252f", pady=12, padx=15)
        nav.pack(fill="x")

        self._nav_buttons = []
        for text, idx in [("Knihy", 0), ("Clenovia", 1), ("Vypozicky", 2)]:
            btn = AnimatedTabButton(nav, text, lambda i=idx: self._switch(i))
            btn.pack(side="left", fill="x", expand=True, padx=6)
            self._nav_buttons.append(btn)

        tk.Frame(self, bg="#2980b9", height=2).pack(fill="x", padx=15)

    def _build_content(self):
        self._content = tk.Frame(self, bg="#ecf0f1")
        self._content.pack(fill="both", expand=True, padx=15, pady=10)

        self.books_tab = ttk.Frame(self._content)
        self.members_tab = ttk.Frame(self._content)
        self.loans_tab = ttk.Frame(self._content)
        self._tabs = [self.books_tab, self.members_tab, self.loans_tab]

        self._build_books_tab()
        self._build_members_tab()
        self._build_loans_tab()

    def _switch(self, index):
        for i, (tab, btn) in enumerate(zip(self._tabs, self._nav_buttons)):
            if i == index:
                tab.pack(fill="both", expand=True)
                btn.select()
            else:
                tab.pack_forget()
                if btn._selected:
                    btn.deselect()

    # ------------------------------------------------------------------ SUB NAV
    def _build_subnav(self, parent, labels):
        nav_bar = tk.Frame(parent, bg="#1e2d3d", pady=10)
        nav_bar.pack(fill="x")

        btn_row = tk.Frame(nav_bar, bg="#1e2d3d")
        btn_row.pack()  # no fill/expand -> naturally centered

        content = tk.Frame(parent)
        content.pack(fill="both", expand=True)

        frames = {label: ttk.Frame(content, padding=15) for label in labels}
        buttons = {}

        def switch(lbl):
            for l, f in frames.items():
                if l == lbl:
                    f.pack(fill="both", expand=True)
                    buttons[l].select()
                else:
                    f.pack_forget()
                    if buttons[l]._selected:
                        buttons[l].deselect()

        for label in labels:
            btn = AnimatedTabButton(
                btn_row, label, lambda l=label: switch(l),
                font_size=10, padx=18, pady=11
            )
            btn.pack(side="left", padx=5)
            buttons[label] = btn

        switch(labels[0])
        return frames

    # ------------------------------------------------------------------ BOOKS
    def _build_books_tab(self):
        frames = self._build_subnav(
            self.books_tab,
            ["Pridat", "Vymazat", "Vyhladat", "Aktualizovat"]
        )
        self._build_book_add(frames["Pridat"])
        self._build_book_delete(frames["Vymazat"])
        self._build_book_search(frames["Vyhladat"])
        self._build_book_update(frames["Aktualizovat"])

    def _build_book_add(self, frame):
        labels = ["Nazov", "ID Autora", "ID Zanru", "ISBN", "Rok vydania", "Pocet kopii"]
        self.book_add_vars = {l: tk.StringVar() for l in labels}

        for i, label in enumerate(labels):
            ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky="w", pady=4)
            ttk.Entry(frame, textvariable=self.book_add_vars[label], width=35).grid(row=i, column=1, sticky="w", pady=4)

        self.book_add_status = ttk.Label(frame, text="")
        self.book_add_status.grid(row=len(labels) + 1, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Button(frame, text="Pridat knihu", command=self._book_add).grid(row=len(labels), column=1, sticky="e", pady=10)

    def _book_add(self):
        v = self.book_add_vars
        try:
            result = self.book.add(
                v["Nazov"].get(),
                int(v["ID Autora"].get()),
                int(v["ID Zanru"].get()),
                v["ISBN"].get(),
                int(v["Rok vydania"].get()),
                int(v["Pocet kopii"].get())
            )
            msg = "Zaznam bol uspesne pridany." if result else "Zaznam sa nepodarilo pridat."
            self.book_add_status.config(text=msg, foreground="green" if result else "red")
        except Exception as e:
            self.book_add_status.config(text=f"Chyba: {e}", foreground="red")

    def _build_book_delete(self, frame):
        ttk.Label(frame, text="ID knihy:").grid(row=0, column=0, sticky="w", pady=4)
        self.book_del_id = tk.StringVar()
        ttk.Entry(frame, textvariable=self.book_del_id, width=20).grid(row=0, column=1, sticky="w")

        self.book_del_status = ttk.Label(frame, text="")
        self.book_del_status.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Button(frame, text="Vymazat knihu", command=self._book_delete).grid(row=1, column=1, sticky="e", pady=10)

    def _book_delete(self):
        try:
            result = self.book.delete(int(self.book_del_id.get()))
            msg = "Zaznam bol uspesne vymazany." if result else "Zaznam s tymto ID neexistuje."
            self.book_del_status.config(text=msg, foreground="green" if result else "red")
        except Exception as e:
            self.book_del_status.config(text=f"Chyba: {e}", foreground="red")

    def _build_book_search(self, frame):
        ttk.Label(frame, text="Hladat:").grid(row=0, column=0, sticky="w")
        self.book_search_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.book_search_var, width=35).grid(row=0, column=1, sticky="w")
        ttk.Button(frame, text="Hladat", command=self._book_search).grid(row=0, column=2, padx=5)

        cols = ("ID", "Nazov", "Autor", "Zaner", "ISBN", "Rok", "Kopie")
        self.book_tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        for col in cols:
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=120)
        self.book_tree.column("ID", width=50)
        self.book_tree.grid(row=1, column=0, columnspan=3, pady=10, sticky="nsew")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=sb.set)
        sb.grid(row=1, column=3, sticky="ns", pady=10)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

    def _book_search(self):
        results = self.book.search(self.book_search_var.get())
        self.book_tree.delete(*self.book_tree.get_children())
        if results:
            for row in results:
                self.book_tree.insert("", "end", values=(row[0], row[1], row[8], row[11], row[4], row[5], row[6]))

    def _build_book_update(self, frame):
        ttk.Label(frame, text="ID knihy:").grid(row=0, column=0, sticky="w", pady=4)
        self.book_upd_id = tk.StringVar()
        ttk.Entry(frame, textvariable=self.book_upd_id, width=20).grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Novy nazov (volitelne):").grid(row=1, column=0, sticky="w", pady=4)
        self.book_upd_title = tk.StringVar()
        ttk.Entry(frame, textvariable=self.book_upd_title, width=35).grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Novy pocet kopii (volitelne):").grid(row=2, column=0, sticky="w", pady=4)
        self.book_upd_copies = tk.StringVar()
        ttk.Entry(frame, textvariable=self.book_upd_copies, width=10).grid(row=2, column=1, sticky="w")

        self.book_upd_status = ttk.Label(frame, text="")
        self.book_upd_status.grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Button(frame, text="Aktualizovat", command=self._book_update).grid(row=3, column=1, sticky="e", pady=10)

    def _book_update(self):
        try:
            title = self.book_upd_title.get() or None
            copies_raw = self.book_upd_copies.get()
            copies = int(copies_raw) if copies_raw else None
            result = self.book.update(int(self.book_upd_id.get()), title=title, copies=copies)
            msg = "Zaznam bol uspesne aktualizovany." if result else "Zaznam s tymto ID neexistuje."
            self.book_upd_status.config(text=msg, foreground="green" if result else "red")
        except Exception as e:
            self.book_upd_status.config(text=f"Chyba: {e}", foreground="red")

    # --------------------------------------------------------------- MEMBERS
    def _build_members_tab(self):
        frames = self._build_subnav(
            self.members_tab,
            ["Registrovat", "Vymazat", "Vyhladat"]
        )
        self._build_member_add(frames["Registrovat"])
        self._build_member_delete(frames["Vymazat"])
        self._build_member_search(frames["Vyhladat"])

    def _build_member_add(self, frame):
        labels = ["Meno", "Priezvisko", "Email"]
        self.member_add_vars = {l: tk.StringVar() for l in labels}

        for i, label in enumerate(labels):
            ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky="w", pady=4)
            ttk.Entry(frame, textvariable=self.member_add_vars[label], width=35).grid(row=i, column=1, sticky="w")

        self.member_add_status = ttk.Label(frame, text="")
        self.member_add_status.grid(row=len(labels) + 1, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Button(frame, text="Registrovat", command=self._member_add).grid(row=len(labels), column=1, sticky="e", pady=10)

    def _member_add(self):
        v = self.member_add_vars
        try:
            result = self.member.add(v["Meno"].get(), v["Priezvisko"].get(), v["Email"].get())
            msg = "Zaznam bol uspesne pridany." if result else "Zaznam sa nepodarilo pridat."
            self.member_add_status.config(text=msg, foreground="green" if result else "red")
        except Exception as e:
            self.member_add_status.config(text=f"Chyba: {e}", foreground="red")

    def _build_member_delete(self, frame):
        ttk.Label(frame, text="ID clena:").grid(row=0, column=0, sticky="w", pady=4)
        self.member_del_id = tk.StringVar()
        ttk.Entry(frame, textvariable=self.member_del_id, width=20).grid(row=0, column=1, sticky="w")

        self.member_del_status = ttk.Label(frame, text="")
        self.member_del_status.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Button(frame, text="Vymazat clena", command=self._member_delete).grid(row=1, column=1, sticky="e", pady=10)

    def _member_delete(self):
        try:
            result = self.member.delete(int(self.member_del_id.get()))
            msg = "Zaznam bol uspesne vymazany." if result else "Zaznam s tymto ID neexistuje."
            self.member_del_status.config(text=msg, foreground="green" if result else "red")
        except Exception as e:
            self.member_del_status.config(text=f"Chyba: {e}", foreground="red")

    def _build_member_search(self, frame):
        ttk.Label(frame, text="Hladat:").grid(row=0, column=0, sticky="w")
        self.member_search_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.member_search_var, width=35).grid(row=0, column=1, sticky="w")
        ttk.Button(frame, text="Hladat", command=self._member_search).grid(row=0, column=2, padx=5)

        cols = ("ID", "Meno", "Priezvisko", "Email", "Registracia")
        self.member_tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        for col in cols:
            self.member_tree.heading(col, text=col)
            self.member_tree.column(col, width=140)
        self.member_tree.column("ID", width=50)
        self.member_tree.grid(row=1, column=0, columnspan=3, pady=10, sticky="nsew")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.member_tree.yview)
        self.member_tree.configure(yscrollcommand=sb.set)
        sb.grid(row=1, column=3, sticky="ns", pady=10)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

    def _member_search(self):
        results = self.member.search(self.member_search_var.get())
        self.member_tree.delete(*self.member_tree.get_children())
        if results:
            for row in results:
                self.member_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))

    # ----------------------------------------------------------------- LOANS
    def _build_loans_tab(self):
        frames = self._build_subnav(
            self.loans_tab,
            ["Pozicat", "Vratit", "Historia"]
        )
        self._build_loan_borrow(frames["Pozicat"])
        self._build_loan_return(frames["Vratit"])
        self._build_loan_history(frames["Historia"])

    def _build_loan_borrow(self, frame):
        ttk.Label(frame, text="ID knihy:").grid(row=0, column=0, sticky="w", pady=4)
        self.loan_book_id = tk.StringVar()
        ttk.Entry(frame, textvariable=self.loan_book_id, width=20).grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="ID clena:").grid(row=1, column=0, sticky="w", pady=4)
        self.loan_member_id = tk.StringVar()
        ttk.Entry(frame, textvariable=self.loan_member_id, width=20).grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Termin vratenia (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", pady=4)
        self.loan_due_date = tk.StringVar()
        ttk.Entry(frame, textvariable=self.loan_due_date, width=20).grid(row=2, column=1, sticky="w")

        self.loan_borrow_status = ttk.Label(frame, text="")
        self.loan_borrow_status.grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Button(frame, text="Pozicat", command=self._loan_borrow).grid(row=3, column=1, sticky="e", pady=10)

    def _loan_borrow(self):
        try:
            result = self.loan.borrow(
                int(self.loan_book_id.get()),
                int(self.loan_member_id.get()),
                self.loan_due_date.get()
            )
            msg = "Kniha bola uspesne pozicana." if result else "Vypozicku sa nepodarilo vytvorit."
            self.loan_borrow_status.config(text=msg, foreground="green" if result else "red")
        except Exception as e:
            self.loan_borrow_status.config(text=f"Chyba: {e}", foreground="red")

    def _build_loan_return(self, frame):
        ttk.Label(frame, text="ID vypozicky:").grid(row=0, column=0, sticky="w", pady=4)
        self.loan_return_id = tk.StringVar()
        ttk.Entry(frame, textvariable=self.loan_return_id, width=20).grid(row=0, column=1, sticky="w")

        self.loan_return_status = ttk.Label(frame, text="")
        self.loan_return_status.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Button(frame, text="Vratit knihu", command=self._loan_return).grid(row=1, column=1, sticky="e", pady=10)

    def _loan_return(self):
        try:
            result = self.loan.return_book(int(self.loan_return_id.get()))
            msg = "Kniha bola uspesne vratena." if result else "Vypozicka s tymto ID neexistuje."
            self.loan_return_status.config(text=msg, foreground="green" if result else "red")
        except Exception as e:
            self.loan_return_status.config(text=f"Chyba: {e}", foreground="red")

    def _build_loan_history(self, frame):
        ttk.Label(frame, text="ID clena:").grid(row=0, column=0, sticky="w")
        self.loan_history_id = tk.StringVar()
        ttk.Entry(frame, textvariable=self.loan_history_id, width=20).grid(row=0, column=1, sticky="w")
        ttk.Button(frame, text="Zobrazit", command=self._loan_history).grid(row=0, column=2, padx=5)

        cols = ("ID", "Kniha", "Vypozicana", "Termin", "Status")
        self.loan_tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        for col in cols:
            self.loan_tree.heading(col, text=col)
            self.loan_tree.column(col, width=140)
        self.loan_tree.column("ID", width=50)
        self.loan_tree.grid(row=1, column=0, columnspan=3, pady=10, sticky="nsew")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.loan_tree.yview)
        self.loan_tree.configure(yscrollcommand=sb.set)
        sb.grid(row=1, column=3, sticky="ns", pady=10)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

    def _loan_history(self):
        try:
            results = self.loan.search(int(self.loan_history_id.get()))
            self.loan_tree.delete(*self.loan_tree.get_children())
            if results:
                for row in results:
                    status = "vratena" if row[4] else "vypozicana"
                    self.loan_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], status))
        except Exception as e:
            messagebox.showerror("Chyba", str(e))


if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()


# ============================================================
# POVODNY KOD
# ============================================================


def show_message(akcia, rowcount):
    spravy = {
        "add":    ("zaznam bol pridany", "zaznam sa nepodarilo pridat"),
        "delete": ("zaznam bol vymazany", "zaznam s tymto ID neexistuje"),
        "update": ("zaznam bol aktualizovany", "zaznam s tymto ID neexistuje"),
        "borrow": ("kniha bola pozicana", "vypozicku sa nepodarilo vytvorit"),
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
