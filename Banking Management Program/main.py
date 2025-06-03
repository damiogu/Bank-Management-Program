import tkinter as tk
from tkinter import messagebox
import tkinter.simpledialog as simpledialog
from tkinter import ttk
import pickle
import os

DATA_FILE = "accounts.pkl"

# Load and save functions
def load_accounts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_accounts(accounts):
    with open(DATA_FILE, "wb") as f:
        pickle.dump(accounts, f)

# Main App Class
class BankSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Management System")
        self.root.geometry("400x450")
        self.root.configure(bg="#f0f4f8")
        self.center_window(400, 450)

        self.accounts = load_accounts()

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
            ("Exit", self.exit_app)
        ]

        for text, command in buttons:
            ttk.Button(self.frame, text=text, command=command).pack(pady=5, fill="x")

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_account_window(self):
        win = tk.Toplevel(self.root)
        win.title("Create Account")
        win.geometry("300x200")
        frame = ttk.Frame(win, padding=10)
        frame.pack()

        ttk.Label(frame, text="Account Number:").grid(row=0, column=0, sticky="e")
        ttk.Label(frame, text="Name:").grid(row=1, column=0, sticky="e")
        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e")
        ttk.Label(frame, text="Initial Deposit:").grid(row=3, column=0, sticky="e")

        acc_no = ttk.Entry(frame)
        name = ttk.Entry(frame)
        password = ttk.Entry(frame, show="*")
        balance = ttk.Entry(frame)

        acc_no.grid(row=0, column=1)
        name.grid(row=1, column=1)
        password.grid(row=2, column=1)
        balance.grid(row=3, column=1)

        def submit():
            num = acc_no.get()
            if num in self.accounts:
                messagebox.showerror("Error", "Account already exists.")
                return
            try:
                self.accounts[num] = {
                    "name": name.get(),
                    "balance": float(balance.get()),
                    "password": password.get(),
                    "transactions": [("Deposit", float(balance.get()))]
                }
                messagebox.showinfo("Success", "Account created.")
                win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input.")

        ttk.Button(frame, text="Create", command=submit).grid(row=4, column=0, columnspan=2, pady=10)

    def authenticate(self, acc_no, prompt="Enter Password"):
        if acc_no not in self.accounts:
            messagebox.showerror("Error", "Account not found.")
            return None
        pwd = simpledialog.askstring("Authentication", prompt, show="*")
        if pwd == self.accounts[acc_no]['password']:
            return self.accounts[acc_no]
        else:
            messagebox.showerror("Error", "Incorrect password.")
            return None

    def deposit_window(self):
        self.simple_transaction_window("Deposit", self.deposit_action)

    def withdraw_window(self):
        self.simple_transaction_window("Withdraw", self.withdraw_action)

    def simple_transaction_window(self, title, action):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("300x150")
        frame = ttk.Frame(win, padding=10)
        frame.pack()

        ttk.Label(frame, text="Account Number:").grid(row=0, column=0)
        ttk.Label(frame, text="Amount:").grid(row=1, column=0)

        acc_no = ttk.Entry(frame)
        amount = ttk.Entry(frame)

        acc_no.grid(row=0, column=1)
        amount.grid(row=1, column=1)

        ttk.Button(frame, text=title, command=lambda: action(acc_no.get(), amount.get(), win)).grid(row=2, column=0, columnspan=2, pady=10)

    def deposit_action(self, acc_no, amt, win):
        acc = self.authenticate(acc_no)
        if not acc:
            return
        try:
            amt = float(amt)
            acc['balance'] += amt
            acc['transactions'].append(("Deposit", amt))
            messagebox.showinfo("Success", "Deposit successful.")
            win.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")

    def withdraw_action(self, acc_no, amt, win):
        acc = self.authenticate(acc_no)
        if not acc:
            return
        try:
            amt = float(amt)
            if acc['balance'] >= amt:
                acc['balance'] -= amt
                acc['transactions'].append(("Withdraw", amt))
                messagebox.showinfo("Success", "Withdrawal successful.")
                win.destroy()
            else:
                messagebox.showerror("Error", "Insufficient funds.")
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")

    def check_balance_window(self):
        self.account_info_window("Check Balance", lambda acc: f"Name: {acc['name']}\nBalance: ${acc['balance']:.2f}")

    def transaction_history_window(self):
        self.account_info_window("Transaction History", lambda acc: "\n".join([f"{t[0]}: ${t[1]:.2f}" for t in acc['transactions']]))

    def account_info_window(self, title, info_func):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("300x120")
        frame = ttk.Frame(win, padding=10)
        frame.pack()

        ttk.Label(frame, text="Account Number:").grid(row=0, column=0)
        acc_no = ttk.Entry(frame)
        acc_no.grid(row=0, column=1)

        def show():
            acc = self.authenticate(acc_no.get(), "Enter Password")
            if acc:
                info = info_func(acc)
                messagebox.showinfo(title, info if info else "No data found.")
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
            acc = self.authenticate(num, "Enter Password to Confirm Deletion")
            if acc:
                confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this account?")
                if confirm:
                    del self.accounts[num]
                    messagebox.showinfo("Deleted", "Account deleted successfully.")
                    win.destroy()

        ttk.Button(frame, text="Delete", command=delete).grid(row=1, column=0, columnspan=2, pady=10)

    def exit_app(self):
        save_accounts(self.accounts)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BankSystemApp(root)
    root.mainloop()
