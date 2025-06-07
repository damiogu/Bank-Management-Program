import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3

DB_FILE = "accounts.db"

# Database Setup
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            acc_no TEXT PRIMARY KEY,
            name TEXT,
            password TEXT,
            balance REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acc_no TEXT,
            type TEXT,
            amount REAL,
            FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
        )
    """)
    conn.commit()
    conn.close()

class BankSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Management System")
        self.root.geometry("400x450")
        self.root.configure(bg="#f0f4f8")
        self.center_window(400, 450)
        init_db()

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=10)
        style.configure("TLabel", font=("Segoe UI", 10))

        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(fill="both", expand=True)

        ttk.Label(self.frame, text="Bank Management System", font=("Segoe UI", 14, "bold")).pack(pady=10)

        buttons = [
            ("Create Account", self.create_account_window),
            ("Deposit", self.deposit_window),
            ("Withdraw", self.withdraw_window),
            ("Check Balance", self.check_balance_window),
            ("Transaction History", self.transaction_history_window),
            ("Delete Account", self.delete_account_window),
            ("Exit", self.root.quit)
        ]

        for text, command in buttons:
            ttk.Button(self.frame, text=text, command=command).pack(pady=5, fill="x")

    def center_window(self, width, height):
        x = int((self.root.winfo_screenwidth() - width) / 2)
        y = int((self.root.winfo_screenheight() - height) / 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def authenticate(self, acc_no, prompt="Enter Password"):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM accounts WHERE acc_no = ?", (acc_no,))
        result = cursor.fetchone()
        conn.close()
        if not result:
            messagebox.showerror("Error", "Account not found.")
            return None
        pwd = simpledialog.askstring("Authentication", prompt, show="*")
        if pwd == result[0]:
            return True
        else:
            messagebox.showerror("Error", "Incorrect password.")
            return None

    def create_account_window(self):
        win = tk.Toplevel(self.root)
        win.title("Create Account")
        win.geometry("300x200")
        frame = ttk.Frame(win, padding=10)
        frame.pack()

        acc_no = ttk.Entry(frame)
        name = ttk.Entry(frame)
        password = ttk.Entry(frame, show="*")
        balance = ttk.Entry(frame)

        for i, text in enumerate(["Account Number", "Name", "Password", "Initial Deposit"]):
            ttk.Label(frame, text=text + ":").grid(row=i, column=0, sticky="e")

        acc_no.grid(row=0, column=1)
        name.grid(row=1, column=1)
        password.grid(row=2, column=1)
        balance.grid(row=3, column=1)

        def submit():
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT acc_no FROM accounts WHERE acc_no = ?", (acc_no.get(),))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Account already exists.")
                    conn.close()
                    return
                bal = float(balance.get())
                cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, ?)",
                               (acc_no.get(), name.get(), password.get(), bal))
                cursor.execute("INSERT INTO transactions (acc_no, type, amount) VALUES (?, ?, ?)",
                               (acc_no.get(), "Deposit", bal))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Account created.")
                win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input.")

        ttk.Button(frame, text="Create", command=submit).grid(row=4, column=0, columnspan=2, pady=10)

    def deposit_window(self):
        self.transaction_window("Deposit")

    def withdraw_window(self):
        self.transaction_window("Withdraw")

    def transaction_window(self, title):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("300x150")
        frame = ttk.Frame(win, padding=10)
        frame.pack()

        acc_no = ttk.Entry(frame)
        amount = ttk.Entry(frame)

        ttk.Label(frame, text="Account Number:").grid(row=0, column=0)
        ttk.Label(frame, text="Amount:").grid(row=1, column=0)

        acc_no.grid(row=0, column=1)
        amount.grid(row=1, column=1)

        def perform():
            if not self.authenticate(acc_no.get()):
                return
            try:
                amt = float(amount.get())
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT balance FROM accounts WHERE acc_no = ?", (acc_no.get(),))
                bal = cursor.fetchone()[0]
                if title == "Withdraw" and amt > bal:
                    messagebox.showerror("Error", "Insufficient funds.")
                else:
                    new_bal = bal + amt if title == "Deposit" else bal - amt
                    cursor.execute("UPDATE accounts SET balance = ? WHERE acc_no = ?", (new_bal, acc_no.get()))
                    cursor.execute("INSERT INTO transactions (acc_no, type, amount) VALUES (?, ?, ?)",
                                   (acc_no.get(), title, amt))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", f"{title} successful.")
                    win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid amount.")

        ttk.Button(frame, text=title, command=perform).grid(row=2, column=0, columnspan=2, pady=10)

    def check_balance_window(self):
        self.simple_view_window("Check Balance", "SELECT name, balance FROM accounts WHERE acc_no = ?",
                                lambda r: f"Name: {r[0]}\nBalance: ${r[1]:.2f}")

    def transaction_history_window(self):
        self.simple_view_window("Transaction History",
                                "SELECT type, amount FROM transactions WHERE acc_no = ?",
                                lambda rows: "\n".join([f"{t}: ${a:.2f}" for t, a in rows]))

    def simple_view_window(self, title, query, format_result):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("300x150")
        frame = ttk.Frame(win, padding=10)
        frame.pack()

        ttk.Label(frame, text="Account Number:").grid(row=0, column=0)
        acc_no = ttk.Entry(frame)
        acc_no.grid(row=0, column=1)

        def show():
            if not self.authenticate(acc_no.get()):
                return
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(query, (acc_no.get(),))
            rows = cursor.fetchall()
            conn.close()
            if not rows:
                messagebox.showinfo(title, "No data found.")
            else:
                messagebox.showinfo(title, format_result(rows[0] if title == "Check Balance" else rows))
            win.destroy()

        ttk.Button(frame, text="View", command=show).grid(row=1, column=0, columnspan=2, pady=10)

    def delete_account_window(self):
        win = tk.Toplevel(self.root)
        win.title("Delete Account")
        win.geometry("300x120")
        frame = ttk.Frame(win, padding=10)
        frame.pack()

        ttk.Label(frame, text="Account Number:").grid(row=0, column=0)
        acc_no = ttk.Entry(frame)
        acc_no.grid(row=0, column=1)

        def delete():
            num = acc_no.get()
            if not self.authenticate(num):
                return
            confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this account?")
            if confirm:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE acc_no = ?", (num,))
                cursor.execute("DELETE FROM accounts WHERE acc_no = ?", (num,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deleted", "Account deleted successfully.")
                win.destroy()

        ttk.Button(frame, text="Delete", command=delete).grid(row=1, column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = BankSystemApp(root)
    root.mainloop()
