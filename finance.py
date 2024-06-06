import tkinter as tk
from tkinter import ttk
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

# Database connection
conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        date DATE,
        category TEXT,
        description TEXT,
        amount REAL
    );
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY,
        date DATE,
        source TEXT,
        amount REAL
    );
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS budget (
        category TEXT PRIMARY KEY,
        amount REAL
    );
""")
conn.commit()

class FinanceManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Персональный финансовый менеджер")

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True)

        self.expense_frame = ttk.Frame(self.tabs)
        self.income_frame = ttk.Frame(self.tabs)
        self.view_frame = ttk.Frame(self.tabs)
        self.budget_frame = ttk.Frame(self.tabs)
        self.report_frame = ttk.Frame(self.tabs)

        self.tabs.add(self.expense_frame, text="Расход")
        self.tabs.add(self.income_frame, text="Доход")
        self.tabs.add(self.view_frame, text="Список транзакций")
        self.tabs.add(self.budget_frame, text="Бюджет")
        self.tabs.add(self.report_frame, text="Статистика")

        self.create_expense_widgets()
        self.create_income_widgets()
        self.create_view_widgets()
        self.create_budget_widgets()
        self.create_report_widgets()

    def create_expense_widgets(self):

        self.expense_date_label = ttk.Label(self.expense_frame, text="Дата")
        self.expense_date_label.pack()
        self.expense_date_entry = ttk.Entry(self.expense_frame)
        self.expense_date_entry.pack()

        self.expense_category_label = ttk.Label(self.expense_frame, text="Категория")
        self.expense_category_label.pack()
        self.expense_category_entry = ttk.Entry(self.expense_frame)
        self.expense_category_entry.pack()

        self.expense_description_label = ttk.Label(self.expense_frame, text="Описание")
        self.expense_description_label.pack()
        self.expense_description_entry = ttk.Entry(self.expense_frame)
        self.expense_description_entry.pack()

        self.expense_amount_label = ttk.Label(self.expense_frame, text="Стоимость")
        self.expense_amount_label.pack()
        self.expense_amount_entry = ttk.Entry(self.expense_frame)
        self.expense_amount_entry.pack()

        self.expense_button = ttk.Button(self.expense_frame, text="Добавить расход", command=self.add_expense)
        self.expense_button.pack()

    def create_income_widgets(self):
        # Create labels and entries
        self.income_date_label = ttk.Label(self.income_frame, text="Дата")
        self.income_date_label.pack()
        self.income_date_entry = ttk.Entry(self.income_frame)
        self.income_date_entry.pack()

        self.income_source_label = ttk.Label(self.income_frame, text="Источник")
        self.income_source_label.pack()
        self.income_source_entry = ttk.Entry(self.income_frame)
        self.income_source_entry.pack()

        self.income_amount_label = ttk.Label(self.income_frame, text="Приход")
        self.income_amount_label.pack()
        self.income_amount_entry = ttk.Entry(self.income_frame)
        self.income_amount_entry.pack()

        self.income_button = ttk.Button(self.income_frame, text="Добавить доход", command=self.add_income)
        self.income_button.pack()

    def create_view_widgets(self):
        
        self.transaction_treeview = ttk.Treeview(self.view_frame, columns=("date", "category", "description", "amount"))
        self.transaction_treeview.pack()

        # Set column headings
        self.transaction_treeview.heading("date", text="Date")
        self.transaction_treeview.heading("category", text="Category")
        self.transaction_treeview.heading("description", text="Description")
        self.transaction_treeview.heading("amount", text="Amount")

        # Create button to delete transaction
        self.delete_button = ttk.Button(self.view_frame, text="Delete", command=self.delete_transaction)
        self.delete_button.pack(side=tk.LEFT)

        # Create button to refresh transactions
        self.refresh_button = ttk.Button(self.view_frame, text="Refresh", command=self.refresh_transactions)
        self.refresh_button.pack(side=tk.LEFT)

        # Create buttons to sort transactions

        self.sort_by_category_button = ttk.Button(self.view_frame, text="Sort by Category", command=lambda: self.sort_transactions("category"))
        self.sort_by_category_button.pack(side=tk.LEFT)

        self.sort_by_amount_button = ttk.Button(self.view_frame, text="Sort by Amount", command=lambda: self.sort_transactions("amount"))
        self.sort_by_amount_button.pack(side=tk.LEFT)

    def refresh_transactions(self):
        # Clear treeview
        self.transaction_treeview.delete(*self.transaction_treeview.get_children())

        # Query database
        cursor.execute("""
            SELECT date, category, description, amount
            FROM (
                SELECT date, category, description, amount
                FROM expenses
                UNION
                SELECT date, source, '', amount
                FROM income
            ) AS transactions
        """)
        transactions = cursor.fetchall()

        # Insert into treeview
        for transaction in transactions:
            self.transaction_treeview.insert("", "end", values=transaction)

    def delete_transaction(self):
        # Get selected item
        selected_item = self.transaction_treeview.selection()[0]

        # Get values from selected item
        values = self.transaction_treeview.item(selected_item, "values")

        # Delete from database
        if values[2] != '':  # expense
            cursor.execute("DELETE FROM expenses WHERE date=? AND category=? AND description=? AND amount=?",
                        (values[0], values[1], values[2], values[3]))
        else:  # income
            cursor.execute("DELETE FROM income WHERE date=? AND source=? AND amount=?",
                        (values[0], values[1], values[3]))

        conn.commit()

        # Refresh transactions
        self.refresh_transactions()

    def sort_transactions(self, column):
        # Clear treeview
        self.transaction_treeview.delete(*self.transaction_treeview.get_children())

        # Query database
        cursor.execute("""
            SELECT date, category, description, amount
            FROM (
                SELECT date, category, description, amount
                FROM expenses
                UNION
                SELECT date, source, '', amount
                FROM income
            ) AS transactions
        """)
        transactions = cursor.fetchall()

        # Convert date strings to datetime objects and sort
        if column == "category":
            transactions.sort(key=lambda x: x[1])
        elif column == "amount":
            transactions.sort(key=lambda x: x[3])

        # Insert into treeview
        for transaction in transactions:
            self.transaction_treeview.insert("", "end", values=transaction)

    def create_budget_widgets(self):
        # Create labels and entries
        self.budget_category_label = ttk.Label(self.budget_frame, text="Category")
        self.budget_category_label.pack()
        self.budget_category_entry = ttk.Entry(self.budget_frame)
        self.budget_category_entry.pack()

        self.budget_amount_label = ttk.Label(self.budget_frame, text="Amount")
        self.budget_amount_label.pack()
        self.budget_amount_entry = ttk.Entry(self.budget_frame)
        self.budget_amount_entry.pack()

        # Create button to set budget
        self.budget_button = ttk.Button(self.budget_frame, text="Set Budget", command=self.set_budget)
        self.budget_button.pack()

    def create_report_widgets(self):
        # Create button to generate report
        self.report_button = ttk.Button(self.report_frame, text="Generate Report", command=self.generate_report)
        self.report_button.pack()

    def add_expense(self):
        # Get values from entries
        date = self.expense_date_entry.get()
        category = self.expense_category_entry.get()
        description = self.expense_description_entry.get()
        amount = float(self.expense_amount_entry.get())

        # Insert into database
        cursor.execute("INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
                       (date, category, description, amount))
        conn.commit()

        # Clear entries
        self.expense_date_entry.delete(0, tk.END)
        self.expense_category_entry.delete(0, tk.END)
        self.expense_description_entry.delete(0, tk.END)
        self.expense_amount_entry.delete(0, tk.END)

    def add_income(self):
        # Get values from entries
        date = self.income_date_entry.get()
        source = self.income_source_entry.get()
        amount = float(self.income_amount_entry.get())

        # Insert into database
        cursor.execute("INSERT INTO income (date, source, amount) VALUES (?, ?, ?)",
                       (date, source, amount))
        conn.commit()

        # Clear entries
        self.income_date_entry.delete(0, tk.END)
        self.income_source_entry.delete(0, tk.END)
        self.income_amount_entry.delete(0, tk.END)

    def set_budget(self):
        # Get values from entries
        category = self.budget_category_entry.get()
        amount = float(self.budget_amount_entry.get())

        # Insert into database
        cursor.execute("INSERT OR REPLACE INTO budget (category, amount) VALUES (?, ?)",
                       (category, amount))
        conn.commit()

        # Clear entries
        self.budget_category_entry.delete(0, tk.END)
        self.budget_amount_entry.delete(0, tk.END)

    def generate_report(self):
        # Query database
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        expenses = cursor.fetchall()

        cursor.execute("SELECT source, SUM(amount) FROM income GROUP BY source")
        revenues = cursor.fetchall()

        # Create pie charts
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        categories = [expense[0] for expense in expenses]
        amounts = [expense[1] for expense in expenses]
        plt.pie(amounts, labels=categories, autopct="%1.1f%%")
        plt.title("Expenses by Category")

        plt.subplot(1, 2, 2)
        sources = [revenue[0] for revenue in revenues]
        amounts = [revenue[1] for revenue in revenues]
        plt.pie(amounts, labels=sources, autopct="%1.1f%%")
        plt.title("Revenues by Source")

        plt.show()
if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceManager(root)
    root.mainloop()