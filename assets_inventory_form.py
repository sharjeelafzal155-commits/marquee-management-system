import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from db.connection import connect_database
from datetime import date

class AssetsInventoryForm(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.conn = connect_database()
        self.selected_id = None
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        heading = tk.Label(self, text="🪑 Assets Inventory Management", font=("Segoe UI", 18, "bold"))
        heading.pack(pady=20)

        # ======= Form Frame =======
        form_frame = tk.LabelFrame(self, text="Asset Details", padx=10, pady=10)
        form_frame.pack(padx=20, pady=10, fill="x")

        # Item Name
        tk.Label(form_frame, text="Item Name:").grid(row=0, column=0, sticky="e")
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(form_frame, textvariable=self.item_var, values=[
            "Plates", "Spoons", "Glasses", "Chairs", "Sofas", "Tables", "Fans", "AC", "Decor Lights"
        ], width=30)
        self.item_combo.grid(row=0, column=1, padx=10, pady=5)
        self.item_combo.set("")

        # Total Quantity
        tk.Label(form_frame, text="Total Quantity:").grid(row=1, column=0, sticky="e")
        self.total_var = tk.IntVar()
        self.total_entry = tk.Entry(form_frame, textvariable=self.total_var, width=33)
        self.total_entry.grid(row=1, column=1, padx=10, pady=5)

        # Reserved
        tk.Label(form_frame, text="Reserved:").grid(row=2, column=0, sticky="e")
        self.reserved_var = tk.IntVar()
        self.reserved_entry = tk.Entry(form_frame, textvariable=self.reserved_var, width=33)
        self.reserved_entry.grid(row=2, column=1, padx=10, pady=5)

        # Broken
        tk.Label(form_frame, text="Broken:").grid(row=3, column=0, sticky="e")
        self.broken_var = tk.IntVar()
        self.broken_entry = tk.Entry(form_frame, textvariable=self.broken_var, width=33)
        self.broken_entry.grid(row=3, column=1, padx=10, pady=5)

        # Unit
        tk.Label(form_frame, text="Unit:").grid(row=4, column=0, sticky="e")
        self.unit_var = tk.StringVar()
        self.unit_combo = ttk.Combobox(form_frame, textvariable=self.unit_var, values=["pcs", "sets", "units"], width=30)
        self.unit_combo.grid(row=4, column=1, padx=10, pady=5)
        self.unit_combo.set("pcs")

        # Date Updated
        tk.Label(form_frame, text="Date Updated:").grid(row=5, column=0, sticky="e")
        self.date_var = tk.StringVar()
        self.date_entry = DateEntry(form_frame, textvariable=self.date_var, date_pattern="yyyy-mm-dd", width=30)
        self.date_entry.set_date(date.today())
        self.date_entry.grid(row=5, column=1, padx=10, pady=5)

        # Notes
        tk.Label(form_frame, text="Notes:").grid(row=6, column=0, sticky="ne")
        self.notes_text = tk.Text(form_frame, height=3, width=32)
        self.notes_text.grid(row=6, column=1, padx=10, pady=5)

        # Buttons
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=7, column=1, pady=10, sticky="e")
        tk.Button(button_frame, text="Add", command=self.add_asset, bg="#198754", fg="white", width=10).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Update", command=self.update_asset, bg="#0d6efd", fg="white", width=10).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Delete", command=self.delete_asset, bg="#dc3545", fg="white", width=10).grid(row=0, column=2, padx=5)

        # ======= Table Frame =======
        table_frame = tk.LabelFrame(self, text="All Assets", padx=10, pady=10)
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Item", "Total", "Reserved", "Broken", "Unit", "Date"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<ButtonRelease-1>", self.select_asset)

        self.load_assets()

    def add_asset(self):
        data = self.get_form_data()
        if not data:
            return
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO assets_inventory (item_name, quantity_total, quantity_reserved,
                quantity_broken, unit, date_updated, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, data)
            self.conn.commit()
            messagebox.showinfo("Success", "Asset added successfully!")
            self.load_assets()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def update_asset(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Please select an asset to update.")
            return
        data = self.get_form_data()
        if not data:
            return
        try:
            cur = self.conn.cursor()
            cur.execute("""
                UPDATE assets_inventory SET
                    item_name=%s, quantity_total=%s, quantity_reserved=%s,
                    quantity_broken=%s, unit=%s, date_updated=%s, notes=%s
                WHERE id=%s
            """, data + (self.selected_id,))
            self.conn.commit()
            messagebox.showinfo("Updated", "Asset updated successfully!")
            self.load_assets()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def delete_asset(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Please select an asset to delete.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this asset?")
        if confirm:
            try:
                cur = self.conn.cursor()
                cur.execute("DELETE FROM assets_inventory WHERE id=%s", (self.selected_id,))
                self.conn.commit()
                messagebox.showinfo("Deleted", "Asset deleted successfully!")
                self.load_assets()
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

    def load_assets(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT id, item_name, quantity_total, quantity_reserved, quantity_broken, unit, date_updated FROM assets_inventory ORDER BY date_updated DESC")
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def select_asset(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, 'values')
            self.selected_id = values[0]
            try:
                cur = self.conn.cursor()
                cur.execute("SELECT * FROM assets_inventory WHERE id=%s", (self.selected_id,))
                data = cur.fetchone()
                if data:
                    self.item_var.set(data[1])
                    self.total_var.set(data[2])
                    self.reserved_var.set(data[3])
                    self.broken_var.set(data[4])
                    self.unit_var.set(data[5])
                    self.date_var.set(data[6])
                    self.notes_text.delete("1.0", "end")
                    self.notes_text.insert("1.0", data[7])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load asset.\n{e}")

    def clear_form(self):
        self.selected_id = None
        self.item_combo.set("")
        self.total_var.set(0)
        self.reserved_var.set(0)
        self.broken_var.set(0)
        self.unit_combo.set("pcs")
        self.date_entry.set_date(date.today())
        self.notes_text.delete("1.0", "end")

    def get_form_data(self):
        try:
            item = self.item_var.get()
            total = self.total_var.get()
            reserved = self.reserved_var.get()
            broken = self.broken_var.get()
            unit = self.unit_var.get()
            date_updated = self.date_var.get()
            notes = self.notes_text.get("1.0", "end").strip()

            if reserved + broken > total:
                raise ValueError("Reserved + Broken cannot exceed Total Quantity.")
            if not item or total < 0:
                raise ValueError("Item name and total quantity are required.")

            return (item, total, reserved, broken, unit, date_updated, notes)
        except Exception as e:
            messagebox.showerror("Input Error", str(e))
            return None



