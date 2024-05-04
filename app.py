import tkinter as tk
from tkinter import ttk
import requests
import os
import sqlite3
from datetime import datetime

class StockTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Tracker")
        self.root.geometry("1200x600")

        self.api_key = "0EVM8ZDMXVUQ9500"
        self.tracking_list = []
        if not os.path.exists("stocks.db"):
            self.create_database()

        self.create_widgets()

    def create_database(self):
        self.db_conn = sqlite3.connect("stocks.db")
        self.db_cursor = self.db_connection.cursor()

        # Add missing 'stock' column to the 'stocks' table
        self.db_cursor.execute("ALTER TABLE stocks ADD COLUMN stock TEXT")
        self.db_connection.commit()

        # Create the 'stocks' table
        self.db_cursor.execute("""
            CREATE TABLE stocks (
                id INTEGER PRIMARY KEY,
                stock TEXT NOT NULL,
                purchase_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                date_purchased DATE NOT NULL,
                current_price REAL NOT NULL,
                profit_loss REAL NOT NULL
            )
            """)
        self.db_connection.commit()

    def create_widgets(self):
        # Create frames
        self.frame_header = tk.Frame(self.root, bg="gray")
        self.frame_header.pack(fill="x")

        self.frame_tracking_list = tk.Frame(self.root, bg="white")
        self.frame_tracking_list.pack(fill="both", expand=True)

        # Create header widgets
        self.label_header = tk.Label(self.frame_header, text="Stock Tracker", font=("Arial", 24), bg="gray")
        self.label_header.pack(pady=10)

        # Create tracking list widgets
        self.treeview = ttk.Treeview(self.frame_tracking_list, columns=("Stock", "Purchase Price", "Quantity", "Current Price", "Profit/Loss (%)"))
        self.treeview.pack(fill="both", expand=True)

        self.treeview.heading("#0", text="Stock")
        self.treeview.heading("Purchase Price", text="Purchase Price")
        self.treeview.heading("Quantity", text="Quantity")
        self.treeview.heading("Current Price", text="Current Price")
        self.treeview.heading("Profit/Loss (%)", text="Profit/Loss (%)")

        # Create add stock button
        self.button_add_stock = tk.Button(self.frame_header, text="Add Stock", command=self.add_stock)
        self.button_add_stock.pack(side="right", padx=10)

        # Create total profit/loss label
        self.label_total_profit_loss = tk.Label(self.frame_header, text="Total Profit/Loss: 0.00%", bg="gray")
        self.label_total_profit_loss.pack(side="right", padx=10)

    def add_stock(self):
        # Create add stock dialog
        dialog = AddStockDialog(self.root, self)
        self.root.wait_window(dialog)

    def update_tracking_list(self, stock, purchase_price, quantity):
        # Get current stock price from Alpha Vantage API
        response = requests.get(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={self.api_key}")
        data = response.json()
        current_price = float(data["Global Quote"]["05. price"])

        # Calculate profit/loss
        profit_loss = (current_price - purchase_price) / purchase_price * 100

        # Add stock to tracking list
        self.tracking_list.append({"Stock": stock, "Purchase Price": purchase_price, "Quantity": quantity, "Current Price": current_price, "Profit/Loss (%)": profit_loss})

        # Update treeview
        self.treeview.insert("", "end", values=(stock, purchase_price, quantity, current_price, profit_loss))

        # Update total profit/loss
        total_profit_loss = sum([item["Profit/Loss(%)"] for item in self.tracking_list])
        self.label_total_profit_loss.config(text=f"Total Profit/Loss: {total_profit_loss:.2f}%")

    def close_position(self, stock):
        # Get the index of the stock in the tracking list
        index = self.tracking_list.index(next(filter(lambda x: x["Stock"] == stock, self.tracking_list)))

        # Get the purchase price and quantity from the database
        self.db_cursor.execute("SELECT purchase_price, quantity FROM stocks WHERE stock=?", (stock,))
        purchase_price, quantity = self.db_cursor.fetchone()

        # Calculate profit/loss
        current_price = self.tracking_list[index]["Current Price"]
        profit_loss = (current_price - purchase_price) / purchase_price * 100

        # Update the profit/loss in the database
        self.db_cursor.execute("UPDATE stocks SET profit_loss=? WHERE stock=?", (profit_loss, stock))
        self.db_connection.commit()

        # Remove the stock from the tracking list
        self.tracking_list.pop(index)

        # Update treeview
        self.treeview.delete(self.treeview.index(self.treeview.focus()))

        # Update total profit/loss
        total_profit_loss = sum([item["Profit/Loss (%)"] for item in self.tracking_list])
        self.label_total_profit_loss.config(text=f"Total Profit/Loss: {total_profit_loss:.2f}%")

    def get_current_price(self, stock_name):
        # Get current stock price from Alpha Vantage API
        response = requests.get(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_name}&apikey={self.api_key}")
        data = response.json()
        print(f"____________{data}__________")
        current_price = float(data["Global Quote"]["05. price"])
        return current_price
    

class AddStockDialog:
    def __init__(self, parent, stock_tracker):
        self.parent = parent
        self.stock_tracker = stock_tracker

        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Add Stock")

        self.create_widgets()

    def create_widgets(self):
        # Create labels and entries
        self.label_stock = tk.Label(self.dialog, text="Stock:")
        self.label_stock.pack()
        self.entry_stock = tk.Entry(self.dialog)
        self.entry_stock.pack()

        self.label_purchase_price = tk.Label(self.dialog, text="Purchase Price:")
        self.label_purchase_price.pack()
        self.entry_purchase_price = tk.Entry(self.dialog)
        self.entry_purchase_price.pack()

        self.label_quantity = tk.Label(self.dialog, text="Quantity:")
        self.label_quantity.pack()
        self.entry_quantity = tk.Entry(self.dialog)
        self.entry_quantity.pack()

        # Create add button
        self.button_add = tk.Button(self.dialog, text="Add", command=self.add_stock)
        self.button_add.pack()

    def add_stock(self):
        # Get stock data from the user
        stock_name = self.entry_stock.get()
        purchase_price = float(self.entry_purchase_price.get())
        quantity = int(self.entry_quantity.get())

        # Get the current price of the stock from the Alpha Vantage API
        current_price = self.stock_tracker.get_current_price(stock_name)

        # Create a dictionary with the stock data
        stock_data = {
            "stock": stock_name,
            "purchase_price": purchase_price,
            "quantity": quantity,
            "date_purchased": datetime.today().strftime("%Y-%m-%d"),
            "current_price": current_price,
            "profit_loss": 0.0,
        }

        # Insert the stock data into the 'stocks' table
        self.stock_tracker.db_cursor.execute("""
            INSERT INTO stocks (stock_name, purchase_price, quantity, date_purchased, current_price, profit_loss)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (stock_data["stock"], stock_data["purchase_price"], stock_data["quantity"], stock_data["date_purchased"], stock_data["current_price"], stock_data["profit_loss"]))

        # Commit the changes and close the connection
        self.stock_tracker.db_conn.commit()
        self.stock_tracker.db_conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = StockTracker(root)
    root.mainloop()