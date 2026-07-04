# -*- coding: utf-8 -*-
# Save as: forms/khaata_fruits_vegs_form.py

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date
from db.connection import connect_database

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class KhaataFruitsVegsForm(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        # Premium Dark Palette Configuration Matrix Matching Catppuccin Mocha Base Theme
        super().__init__(master, fg_color="#1e1e2e", **kwargs)
        self.master = master
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.selected_id = None
        
        # Enforce database schema architecture before UI construction
        self.ensure_database_schema_layers()
        
        # Initialize UI reactive input tracking state handlers
        self.initialize_form_variables()
        
        # Build UI Screen Grid Layout Elements
        self.setup_ui_components()
        
        # Fetch initial datasets to load tables and dropdowns
        self.refresh_booking_dropdown_list()
        self.refresh_table_dataset()

    def ensure_database_schema_layers(self):
        """Creates or alters tables to enforce strict double-entry system rules architecture."""
        conn = connect_database()
        if not conn:
            return
        try:
            cur = conn.cursor()
            
            # 1. Ensure sub-khaata table exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS khaata_fruits_vegs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    category VARCHAR(100) DEFAULT 'Fruits & Vegetables',
                    item_name VARCHAR(100) NOT NULL,
                    quantity DECIMAL(10,2) NOT NULL,
                    unit VARCHAR(20) DEFAULT 'kg',
                    price_per_unit DECIMAL(10,2) NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    supplier_name VARCHAR(100) DEFAULT 'Market Supplier',
                    paid_amount DECIMAL(10,2) DEFAULT 0.00,
                    remaining_balance DECIMAL(10,2) DEFAULT 0.00,
                    purchase_date DATE NOT NULL,
                    booking_id INT NULL,
                    payment_status VARCHAR(50) DEFAULT 'Pending',
                    payment_method VARCHAR(50) DEFAULT 'Cash',
                    reference_no VARCHAR(100) NULL,
                    remarks TEXT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB;
            """)
            
            # 2. Ensure main expenses table exists for tracking core ledger sync routing
            cur.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    expense_type VARCHAR(100) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    expense_date DATE NOT NULL,
                    paid_by VARCHAR(100) NULL,
                    payment_method VARCHAR(50) NOT NULL,
                    reference_no VARCHAR(100) NULL,
                    attachment_path VARCHAR(255) NULL,
                    status VARCHAR(50) NOT NULL,
                    description TEXT NULL,
                    source_table VARCHAR(50) NULL,
                    source_id INT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB;
            """)
            
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Schema Boot Failure", f"Database engine rejected layout mapping:\n{str(e)}")

    def initialize_form_variables(self):
        """Initializes secure runtime reactive variables for layout tracking pipelines."""
        self.v_item_name = tk.StringVar()
        self.v_quantity = tk.StringVar(value="0")
        self.v_unit = tk.StringVar(value="kg")
        self.v_price = tk.StringVar(value="0")
        self.v_total_amount = tk.StringVar(value="0.00")
        self.v_supplier = tk.StringVar()
        self.v_paid_amount = tk.StringVar(value="0")
        self.v_balance = tk.StringVar(value="0.00")
        self.v_booking_filter = tk.StringVar(value="None / General Stock")
        self.v_payment_method = tk.StringVar(value="Cash")
        self.v_payment_status = tk.StringVar(value="Pending")
        self.v_ref_no = tk.StringVar()
        self.v_remarks = tk.StringVar()
        self.v_search = tk.StringVar()
        
        # Auto-calculating hooks to keep numerical entries synced on key strikes
        self.v_quantity.trace_add("write", lambda *args: self.calculate_financial_metrics())
        self.v_price.trace_add("write", lambda *args: self.calculate_financial_metrics())
        self.v_paid_amount.trace_add("write", lambda *args: self.calculate_financial_metrics())
        
        # Mappings list arrays cache maps
        self.booking_id_map = {}

    def calculate_financial_metrics(self):
        """Processes transactional math tracking instantly without dropping precision handles."""
        try:
            qty = float(self.v_quantity.get()) if self.v_quantity.get() else 0.0
            rate = float(self.v_price.get()) if self.v_price.get() else 0.0
            paid = float(self.v_paid_amount.get()) if self.v_paid_amount.get() else 0.0
            
            total = qty * rate
            balance = total - paid
            
            self.v_total_amount.set(f"{total:.2f}")
            self.v_balance.set(f"{balance:.2f}")
            
            # Auto update payment status enum variable flags contextually
            if total == 0:
                self.v_payment_status.set("Pending")
            elif paid >= total:
                self.v_payment_status.set("Paid")
            elif paid > 0:
                self.v_payment_status.set("Partial")
            else:
                self.v_payment_status.set("Pending")
        except ValueError:
            pass # Suppress trace calculation parsing faults during typing shifts

    def setup_ui_components(self):
        """Constructs layout matrix interfaces splitting form data captures and records data views."""
        # Main Title Header Banner
        title_lbl = ctk.CTkLabel(
            self, text="FRUITS & VEGETABLES KHAATA LEDGER SYSTEM", 
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"), text_color="#cba6f7"
        )
        title_lbl.pack(pady=(0, 15))
        
        # Container splitting control cards vs telemetry views
        content_workspace = ctk.CTkFrame(self, fg_color="transparent")
        content_workspace.pack(fill="both", expand=True)
        
        # Left Control Input Frame Layout Card Block
        input_panel = ctk.CTkScrollableFrame(content_workspace, width=380, fg_color="#313244", label_text="Log Entry Parameters")
        input_panel.configure(label_text_color="#cdd6f4", label_font=("Consolas", 14, "bold"))
        input_panel.pack(side="left", fill="both", expand=False, padx=(0, 15))
        
        # Build systematic input widgets inside left workspace matrix panel
        self.create_input_widget_fields(input_panel)
        
        # Right Operational Telemetry Data Engine Views Block
        view_panel = ctk.CTkFrame(content_workspace, fg_color="#181825")
        view_panel.pack(side="right", fill="both", expand=True)
        
        # Telemetry Search Filter Utility Area bar Layout
        search_bar = ctk.CTkFrame(view_panel, fg_color="transparent")
        search_bar.pack(fill="x", padx=15, pady=10)
        
        search_ent = ctk.CTkEntry(
            search_bar, placeholder_text="Search item name or supplier...", 
            textvariable=self.v_search, width=280, font=("Consolas", 12)
        )
        search_ent.pack(side="left", padx=(0, 10))
        self.v_search.trace_add("write", lambda *args: self.refresh_table_dataset())
        
        btn_export = ctk.CTkButton(
            search_bar, text="Export Workspace Data", fg_color="#a6e3a1", hover_color="#94e2d5",
            text_color="#11111b", font=("Consolas", 12, "bold"), command=self.execute_excel_export_matrix
        )
        btn_export.pack(side="right")
        
        # Structured tabular representation engine via generic legacy tree element UI
        table_container = ctk.CTkFrame(view_panel, fg_color="#1e1e2e")
        table_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.setup_telemetry_table_grid(table_container)

    def create_input_widget_fields(self, parent):
        """Sequentially generates operational forms controls layers."""
        # 1. Linked Booking Event Assignment
        ctk.CTkLabel(parent, text="Link Event/Booking reference:", text_color="#a6adc8").pack(anchor="w", pady=(5,0))
        self.cb_booking = ctk.CTkComboBox(parent, values=["None / General Stock"], variable=self.v_booking_filter, width=340)
        self.cb_booking.pack(pady=5)
        
        # 2. Item description string name
        ctk.CTkLabel(parent, text="Item Name / Description:", text_color="#a6adc8").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(parent, textvariable=self.v_item_name, placeholder_text="e.g., Seasonal Fruits, Salad Mix", width=340).pack(pady=5)
        
        # 3. Numeric tracking: Volume Quantities vs Measurement metric units
        qty_unit_row = ctk.CTkFrame(parent, fg_color="transparent")
        qty_unit_row.pack(fill="x", pady=5)
        
        lbl_q = ctk.CTkFrame(qty_unit_row, fg_color="transparent")
        lbl_q.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(lbl_q, text="Quantity:", text_color="#a6adc8").pack(anchor="w")
        ctk.CTkEntry(lbl_q, textvariable=self.v_quantity, width=160).pack(anchor="w", pady=2)
        
        lbl_u = ctk.CTkFrame(qty_unit_row, fg_color="transparent")
        lbl_u.pack(side="right", fill="x", expand=True)
        ctk.CTkLabel(lbl_u, text="Unit scale:", text_color="#a6adc8").pack(anchor="w")
        ctk.CTkComboBox(lbl_u, values=["kg", "crate", "box", "dozen", "bundle"], variable=self.v_unit, width=160).pack(anchor="e", pady=2)
        
        # 4. Item operational unit metrics charge rates
        ctk.CTkLabel(parent, text="Purchase Rate (Per Unit Price):", text_color="#a6adc8").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(parent, textvariable=self.v_price, width=340).pack(pady=5)
        
        # 5. Financial absolute totals view card layout (ReadOnly Layer Block)
        ctk.CTkLabel(parent, text="Calculated Net Valuation Total:", text_color="#a6adc8").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(parent, textvariable=self.v_total_amount, state="readonly", width=340, text_color="#f9e2af", font=("Consolas", 13, "bold")).pack(pady=5)
        
        # 6. Supplier details profile allocation
        ctk.CTkLabel(parent, text="Supplier Merchant Identity Name:", text_color="#a6adc8").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(parent, textvariable=self.v_supplier, placeholder_text="e.g., Sabzi Mandi vendor, Sabir Fruits Shop", width=340).pack(pady=5)
        
        # 7. Disbursed liquidity paid volumes parameters tracking
        ctk.CTkLabel(parent, text="Disbursed Capital (Paid Amount):", text_color="#a6adc8").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(parent, textvariable=self.v_paid_amount, width=340).pack(pady=5)
        
        # 8. Unsettled balance ledger monitoring tracking
        ctk.CTkLabel(parent, text="Outstanding Balance (Remaining Debt):", text_color="#a6adc8").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(parent, textvariable=self.v_balance, state="readonly", width=340, text_color="#f38ba8", font=("Consolas", 13, "bold")).pack(pady=5)
        
        # 9. Calendar transactional date picker selection
        ctk.CTkLabel(parent, text="Purchase Timeline Logging Date:", text_color="#a6adc8").pack(anchor="w", pady=(5,0))
        self.dt_purchase = DateEntry(parent, width=45, background="#313244", foreground="#cdd6f4", borderwidth=2, date_pattern="yyyy-mm-dd")
        self.dt_purchase.pack(pady=8)
        
        # 10. Financial channel settlement execution channels configuration selector
        ctk.CTkLabel(parent, text="Disbursement Channel (Payment Method):", text_color="#a6adc8").pack(anchor="w", pady=(5,0))
        ctk.CTkComboBox(parent, values=["Cash", "Bank Transfer", "JazzCash", "Easypaisa", "Cheque"], variable=self.v_payment_method, width=340).pack(pady=5)
        
        # 11. Core payment audit validation logging data field strings
        ctk.CTkLabel(parent, text="Reference/Audit receipt number identifier:", text_color="#a6adc8").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(parent, textvariable=self.v_ref_no, placeholder_text="Cheque reference no or transaction ID", width=340).pack(pady=5)
        
        # 12. Context narrative notes block
        ctk.CTkLabel(parent, text="Operational Logs Notes / Remarks:", text_color="#a6adc8").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(parent, textvariable=self.v_remarks, placeholder_text="Event specific demands, quality review notes", width=340).pack(pady=5)
        
        # Action Operational Framework Command Pipeline buttons matrix grid cluster
        btn_panel = ctk.CTkFrame(parent, fg_color="transparent")
        btn_panel.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_panel, text="COMMIT LOG", fg_color="#cba6f7", hover_color="#b4befe", text_color="#11111b", font=("Consolas", 12, "bold"), width=105, command=self.execute_save_transaction_record).grid(row=0, column=0, padx=2)
        ctk.CTkButton(btn_panel, text="REWRITE DATA", fg_color="#fab387", hover_color="#f9e2af", text_color="#11111b", font=("Consolas", 12, "bold"), width=105, command=self.execute_update_transaction_record).grid(row=0, column=1, padx=2)
        ctk.CTkButton(btn_panel, text="WIPE RECORD", fg_color="#f38ba8", hover_color="#eba0ac", text_color="#11111b", font=("Consolas", 12, "bold"), width=105, command=self.execute_purge_transaction_record).grid(row=0, column=2, padx=2)
        ctk.CTkButton(parent, text="FLUSH FORM CONTROL PANELS", fg_color="#313244", hover_color="#45475a", text_color="#cdd6f4", font=("Consolas", 11), width=340, command=self.clear_form_fields_state).pack(pady=(0, 10))

    def setup_telemetry_table_grid(self, parent):
        """Embeds legacy ttk TreeView structural components matrix overlaid with style modifications."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e1e2e", foreground="#cdd6f4", fieldbackground="#1e1e2e", rowheight=28, font=("Consolas", 10))
        style.map("Treeview", background=[("selected", "#45475a")], foreground=[("selected", "#cba6f7")])
        style.configure("Treeview.Heading", background="#313244", foreground="#cdd6f4", borderwidth=0, font=("Consolas", 11, "bold"))
        
        cols = ("id", "item", "qty", "unit", "rate", "total", "supplier", "paid", "balance", "date", "status")
        self.ledger_table = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        
        self.ledger_table.heading("id", text="ID")
        self.ledger_table.heading("item", text="Item Description")
        self.ledger_table.heading("qty", text="Quantity")
        self.ledger_table.heading("unit", text="Unit")
        self.ledger_table.heading("rate", text="Rate")
        self.ledger_table.heading("total", text="Net Price")
        self.ledger_table.heading("supplier", text="Supplier Merchant")
        self.ledger_table.heading("paid", text="Paid Out")
        self.ledger_table.heading("balance", text="Balance Due")
        self.ledger_table.heading("date", text="Logged Date")
        self.ledger_table.heading("status", text="Audit Status")
        
        self.ledger_table.column("id", width=40, anchor="center")
        self.ledger_table.column("item", width=140, anchor="w")
        self.ledger_table.column("qty", width=70, anchor="center")
        self.ledger_table.column("unit", width=50, anchor="center")
        self.ledger_table.column("rate", width=70, anchor="e")
        self.ledger_table.column("total", width=90, anchor="e")
        self.ledger_table.column("supplier", width=130, anchor="w")
        self.ledger_table.column("paid", width=80, anchor="e")
        self.ledger_table.column("balance", width=80, anchor="e")
        self.ledger_table.column("date", width=95, anchor="center")
        self.ledger_table.column("status", width=80, anchor="center")
        
        v_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.ledger_table.yview)
        h_scroll = ttk.Scrollbar(parent, orient="horizontal", command=self.ledger_table.xview)
        self.ledger_table.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.ledger_table.pack(side="top", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y", before=self.ledger_table)
        h_scroll.pack(side="bottom", fill="x")
        
        self.ledger_table.bind("<<TreeviewSelect>>", self.on_record_row_selected)

    def refresh_booking_dropdown_list(self):
        """Fetches pipeline references mapping actively booked wedding arrays elements."""
        conn = connect_database()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, customer_name, event_date, event_type FROM bookings WHERE booking_status  != 'Cancelled' ORDER BY event_date DESC")
            records = cur.fetchall()
            conn.close()
            
            dropdown_opts = ["None / General Stock"]
            self.booking_id_map.clear()
            
            for row in records:
                display_str = f"ID: {row[0]} | {row[1]} - {row[2]} ({row[3]})"
                dropdown_opts.append(display_str)
                self.booking_id_map[display_str] = row[0]
                
            self.cb_booking.configure(values=dropdown_opts)
        except Exception as e:
            print(f"[Core Logging Exception] Dropdown array indexing loop failed: {str(e)}")

    def refresh_table_dataset(self):
        """Pulls transaction stream records arrays matching filter queries mapping matrices rows."""
        conn = connect_database()
        if not conn:
            return
        try:
            cur = conn.cursor()
            search_query = self.v_search.get().strip()
            
            if search_query:
                sql = """
                    SELECT id, item_name, quantity, unit, price_per_unit, total_amount, supplier_name, paid_amount, remaining_balance, purchase_date, payment_status 
                    FROM khaata_fruits_vegs 
                    WHERE item_name LIKE %s OR supplier_name LIKE %s 
                    ORDER BY purchase_date DESC, id DESC
                """
                cur.execute(sql, (f"%{search_query}%", f"%{search_query}%"))
            else:
                sql = """
                    SELECT id, item_name, quantity, unit, price_per_unit, total_amount, supplier_name, paid_amount, remaining_balance, purchase_date, payment_status 
                    FROM khaata_fruits_vegs 
                    ORDER BY purchase_date DESC, id DESC
                """
                cur.execute(sql)
                
            records = cur.fetchall()
            conn.close()
            
            # Flush legacy visual buffer markers mapping grid rows
            for item in self.ledger_table.get_children():
                self.ledger_table.delete(item)
                
            # Append fetched tuples rows mapped cleanly onto presentation grid elements
            for row in records:
                self.ledger_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Telemetry Data Fetch Interrupted", str(e))

    def execute_save_transaction_record(self):
        """Executes full double-entry transaction layer writing to sub-khaata and main expenses ledger."""
        if not self.v_item_name.get().strip():
            messagebox.showerror("Validation Boundary Alert", "Item Description identifier column text cannot be blank.")
            return
            
        try:
            qty = float(self.v_quantity.get())
            rate = float(self.v_price.get())
            paid = float(self.v_paid_amount.get())
        except ValueError:
            messagebox.showerror("Numerical Parsing Exception", "Quantity, Charge rates, and disbursed metrics must evaluate to decimal weights.")
            return

        # Map current linking index structures mapping variables selections targets
        bk_selection = self.v_booking_filter.get()
        target_booking_id = self.booking_id_map.get(bk_selection, None)
        
        conn = connect_database()
        if not conn:
            return
            
        try:
            cur = conn.cursor()
            
            # --- LAYER 1: INSERT INTO SUB-KHAATA TABLE ---
            sql_sub = """
                INSERT INTO khaata_fruits_vegs 
                (item_name, quantity, unit, price_per_unit, total_amount, supplier_name, paid_amount, remaining_balance, purchase_date, booking_id, payment_status, payment_method, reference_no, remarks) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params_sub = (
                self.v_item_name.get().strip(), qty, self.v_unit.get(), rate, float(self.v_total_amount.get()),
                self.v_supplier.get().strip() or "Market Supplier", paid, float(self.v_balance.get()),
                self.dt_purchase.get_date(), target_booking_id, self.v_payment_status.get(),
                self.v_payment_method.get(), self.v_ref_no.get().strip() or None, self.v_remarks.get().strip() or None
            )
            cur.execute(sql_sub, params_sub)
            generated_source_id = cur.lastrowid
            
            # --- LAYER 2: SYNC TO MAIN EXPENSES TABLE (Shared Table Pattern) ---
            # Double entry rules mandate total valuation of allocation drops as core expense metric weight
            sql_exp = """
                INSERT INTO expenses 
                (expense_type, amount, expense_date, paid_by, payment_method, reference_no, status, description, source_table, source_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            expense_desc = f"Item: {self.v_item_name.get().strip()} | Qty: {qty} {self.v_unit.get()} | Supplier: {self.v_supplier.get().strip() or 'Market Supplier'}"
            params_exp = (
                "Fruits & Vegetables Khaata", float(self.v_total_amount.get()), self.dt_purchase.get_date(),
                self.v_supplier.get().strip() or "Market Supplier", self.v_payment_method.get(),
                self.v_ref_no.get().strip() or None, self.v_payment_status.get(), expense_desc,
                "khaata_fruits_vegs", generated_source_id
            )
            cur.execute(sql_exp, params_exp)
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("System Registry Ledger Alpha", "Fruits and Vegetables purchase transactional arrays saved securely and mirrored to Core Expenses.")
            self.clear_form_fields_state()
            self.refresh_table_dataset()
            
            # Trigger KPI dashboard calculations matrix reload hooks if bound under main master canvas framework
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
        except Exception as e:
            messagebox.showerror("Execution Framework Write Halt", str(e))

    def execute_update_transaction_record(self):
        """Modifies and synchronizes transaction states across both sub-khaata and main operational ledgers."""
        if not self.selected_id:
            messagebox.showerror("Selection Context Missing", "Please select a target row sequence inside telemetry display table before invoking rewrite actions.")
            return
            
        try:
            qty = float(self.v_quantity.get())
            rate = float(self.v_price.get())
            paid = float(self.v_paid_amount.get())
        except ValueError:
            messagebox.showerror("Numerical Parsing Exception", "Quantity, Rates, and disbursement parameters must pass float evaluation rules constraints.")
            return

        bk_selection = self.v_booking_filter.get()
        target_booking_id = self.booking_id_map.get(bk_selection, None)
        
        conn = connect_database()
        if not conn:
            return
            
        try:
            cur = conn.cursor()
            
            # --- LAYER 1: UPDATE SUB-KHAATA ENTRY ---
            sql_sub = """
                UPDATE khaata_fruits_vegs 
                SET item_name=%s, quantity=%s, unit=%s, price_per_unit=%s, total_amount=%s, supplier_name=%s, paid_amount=%s, remaining_balance=%s, purchase_date=%s, booking_id=%s, payment_status=%s, payment_method=%s, reference_no=%s, remarks=%s 
                WHERE id=%s
            """
            params_sub = (
                self.v_item_name.get().strip(), qty, self.v_unit.get(), rate, float(self.v_total_amount.get()),
                self.v_supplier.get().strip() or "Market Supplier", paid, float(self.v_balance.get()),
                self.dt_purchase.get_date(), target_booking_id, self.v_payment_status.get(),
                self.v_payment_method.get(), self.v_ref_no.get().strip() or None, self.v_remarks.get().strip() or None,
                self.selected_id
            )
            cur.execute(sql_sub, params_sub)
            
            # --- LAYER 2: UPDATE CORE EXPENSES LOG VIA SOURCE MAPPING INDEX LOOKUPS ---
            sql_exp = """
                UPDATE expenses 
                SET amount=%s, expense_date=%s, paid_by=%s, payment_method=%s, reference_no=%s, status=%s, description=%s 
                WHERE source_table='khaata_fruits_vegs' AND source_id=%s
            """
            expense_desc = f"UPDATED >> Item: {self.v_item_name.get().strip()} | Qty: {qty} {self.v_unit.get()} | Supplier: {self.v_supplier.get().strip() or 'Market Supplier'}"
            params_exp = (
                float(self.v_total_amount.get()), self.dt_purchase.get_date(), self.v_supplier.get().strip() or "Market Supplier",
                self.v_payment_method.get(), self.v_ref_no.get().strip() or None, self.v_payment_status.get(),
                expense_desc, self.selected_id
            )
            cur.execute(sql_exp, params_exp)
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Registry Sync Ledger Beta", "Target transactional row entry state updated perfectly inside sub-channels and primary expense routers.")
            self.clear_form_fields_state()
            self.refresh_table_dataset()
            
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
        except Exception as e:
            messagebox.showerror("Execution Framework Update Halt", str(e))

    def execute_purge_transaction_record(self):
        """Drops logging rows safely across all interconnected storage layers to protect structural math metrics."""
        if not self.selected_id:
            messagebox.showerror("Selection Context Missing", "Target row identifier pointer reference context dropped. Re-select tree element row.")
            return
            
        action_confirmation = messagebox.askyesno("Destructive Security Request", "Are you sure you want to drop this transaction row permanently? This will clear the entry from both sub-khaata and primary expenses table.")
        if not action_confirmation:
            return
            
        conn = connect_database()
        if not conn:
            return
            
        try:
            cur = conn.cursor()
            
            # --- LAYER 1: DROP FROM SUB-KHAATA TABLE ---
            cur.execute("DELETE FROM khaata_fruits_vegs WHERE id = %s", (self.selected_id,))
            
            # --- LAYER 2: DROP CORRESPONDING LOG FROM MAIN EXPENSES TABLE ---
            cur.execute("DELETE FROM expenses WHERE source_table = 'khaata_fruits_vegs' AND source_id = %s", (self.selected_id,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Purge Successful", "Row entry references destroyed completely across sub-khaata and main expense ledger pools.")
            self.clear_form_fields_state()
            self.refresh_table_dataset()
            
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
        except Exception as e:
            messagebox.showerror("Purge Execution Interrupted", str(e))

    def on_record_row_selected(self, event):
        """Catches user mouse cursor clicks targeting operational grids pulling state arrays directly onto controls variables fields."""
        selected_items_nodes = self.ledger_table.selection()
        if not selected_items_nodes:
            return
            
        row_tuple_values = self.ledger_table.item(selected_items_nodes[0], "values")
        
        # Populate raw values elements array context parameters safely
        self.selected_id = row_tuple_values[0]
        self.v_item_name.set(row_tuple_values[1])
        self.v_quantity.set(str(row_tuple_values[2]))
        self.v_unit.set(row_tuple_values[3])
        self.v_price.set(str(row_tuple_values[4]))
        self.v_total_amount.set(str(row_tuple_values[5]))
        self.v_supplier.set(row_tuple_values[6])
        self.v_paid_amount.set(str(row_tuple_values[7]))
        self.v_balance.set(str(row_tuple_values[8]))
        self.dt_purchase.set_date(row_tuple_values[9])
        self.v_payment_status.set(row_tuple_values[10])
        
        # Pull extended metadata parameters (remarks, reference strings, mapping tracking handles) direct via backend database queries
        conn = connect_database()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT booking_id, payment_method, reference_no, remarks FROM khaata_fruits_vegs WHERE id = %s", (self.selected_id,))
                metadata = cur.fetchone()
                conn.close()
                
                if metadata:
                    b_id = metadata[0]
                    self.v_payment_method.set(metadata[1])
                    self.v_ref_no.set(metadata[2] if metadata[2] else "")
                    self.v_remarks.set(metadata[3] if metadata[3] else "")
                    
                    # Reverse synchronize booking combo selection text matching cached IDs arrays targets
                    matched_dropdown_string = "None / General Stock"
                    if b_id:
                        for display_text, mapping_id in self.booking_id_map.items():
                            if mapping_id == b_id:
                                matched_dropdown_string = display_text
                                break
                    self.v_booking_filter.set(matched_dropdown_string)
            except Exception as e:
                print(f"[Core Selection Fetch Warning] Analytical logging mapping indexing mismatch: {str(e)}")

    def clear_form_fields_state(self):
        """Flushes storage handles arrays variables pointers cleanly to start a fresh input session."""
        self.selected_id = None
        self.v_item_name.set("")
        self.v_quantity.set("0")
        self.v_unit.set("kg")
        self.v_price.set("0")
        self.v_total_amount.set("0.00")
        self.v_supplier.set("")
        self.v_paid_amount.set("0")
        self.v_balance.set("0.00")
        self.v_payment_method.set("Cash")
        self.v_payment_status.set("Pending")
        self.v_ref_no.set("")
        self.v_remarks.set("")
        self.v_booking_filter.set("None / General Stock")
        self.dt_purchase.set_date(date.today())
        self.ledger_table.selection_remove(self.ledger_table.selection())

    def execute_excel_export_matrix(self):
        """Converts database arrays structures to target desktop storage files maps matrices layers."""
        conn = connect_database()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM khaata_fruits_vegs ORDER BY purchase_date DESC")
            dataset = cur.fetchall()
            headers = [col_desc[0] for col_desc in cur.description]
            conn.close()
            
            save_dest_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx", 
                filetypes=[("Excel Matrix Data Worksheet","*.xlsx"), ("CSV Flat Sheet Streams","*.csv")]
            )
            if not save_dest_path:
                return
            
            if save_dest_path.endswith(".xlsx") and PANDAS_AVAILABLE:
                pd.DataFrame(dataset, columns=headers).to_excel(save_dest_path, index=False)
            else:
                import csv
                with open(save_dest_path, "w", newline='', encoding='utf-8') as flat_file:
                    writer = csv.writer(flat_file)
                    writer.writerow(headers)
                    writer.writerows(dataset)
            messagebox.showinfo("Export Successful", f"Data logs sheet structured perfectly inside warehouse node:\n{save_dest_path}")
        except Exception as serialization_fault:
            messagebox.showerror("Export Interrupted", str(serialization_fault))