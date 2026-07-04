# -*- coding: utf-8 -*-
# Save as: forms/expense_form.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date
import os
from db.connection import connect_database

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# ==========================================================================
# ENTERPRISE CONSTANTS DEFINITIONS & ENUMS
# ==========================================================================
EXPENSE_TYPES = [
    "Utilities (Electricity/Gas)", 
    "Staff Salary", 
    "Maintenance & Repairs", 
    "Poultry (Chicken) Khaata", 
    "Meat (Mutton/Beef) Khaata", 
    "Dairy & Milk Khaata", 
    "Karyana Inventory", 
    "Cold Drinks Khaata",
    "Fruits & Vegetables Khaata",
    "Marketing", 
    "Misc"
]
PAYMENT_METHODS = ["Cash", "Bank Transfer", "JazzCash", "Easypaisa", "Cheque"]
STATUS_TYPES = ["Paid", "Pending", "Partial"]


class ExpenseForm(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        """
        Initializes the Centralized Expense Core Module.
        Designed with a split-screen matrix layout matching the Booking Engine structure.
        """
        super().__init__(master, fg_color="#1e1e2e", **kwargs)
        self.master = master
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Operational Pointers & Trackers
        self.selected_expense_id = None
        self.attachment_path = None
        self.event_map = {}
        
        # Enforce Database Architecture State Mapping
        self.ensure_database_integrity_layers()
        
        # Reactive Data Slots Assignments
        self.initialize_secure_variables()
        
        # UI Presentation Build Matrix
        self.setup_ui_layout_left()
        self.setup_ui_layout_right()
        
        # Real-time Synchronizations Pipelines
        self.load_active_events_dropdown()
        self.refresh_table_data()

    def ensure_database_integrity_layers(self):
        """
        Guarantees core expenses tables structures match transactional specifications.
        Safe execution prevents system crashing on bootup sequences.
        """
        conn = connect_database()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    expense_type VARCHAR(100) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    expense_date DATE NOT NULL,
                    payment_method VARCHAR(50) NOT NULL,
                    paid_by VARCHAR(100) NOT NULL,
                    reference_no VARCHAR(100) DEFAULT NULL,
                    status VARCHAR(50) DEFAULT 'Paid',
                    attachment_path VARCHAR(255) DEFAULT NULL,
                    notes TEXT DEFAULT NULL,
                    booking_id INT DEFAULT NULL,
                    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            conn.commit()
            conn.close()
        except Exception as integrity_fault:
            print(f"[Core Schema Sync Error] Check structural mappings variables: {integrity_fault}")

    def initialize_secure_variables(self):
        """Instantiates Tkinter structural variables for live input UI data bindings."""
        self.expense_type = tk.StringVar(value=EXPENSE_TYPES[0])
        self.amount = tk.StringVar(value="0")
        self.payment_method = tk.StringVar(value=PAYMENT_METHODS[0])
        self.paid_by = tk.StringVar()
        self.reference_no = tk.StringVar()
        self.status = tk.StringVar(value=STATUS_TYPES[0])
        self.linked_event = tk.StringVar(value="None / General Expense")
        
        # Core Monitoring Filters Data Handling
        self.search_query = tk.StringVar()
        self.filter_type = tk.StringVar(value="All Types")

    def setup_ui_layout_left(self):
        """
        Configures Left Workspace: Central Expense Studio Entry Panel.
        Builds inputs, combobox components, scroll pads smoothly.
        """
        self.grid_columnconfigure(0, weight=4)  # Left Control Frame
        self.grid_columnconfigure(1, weight=5)  # Right Viewport Ledger Table Frame
        self.grid_rowconfigure(0, weight=1)

        self.left_studio = ctk.CTkFrame(self, fg_color="#313244", corner_radius=15)
        self.left_studio.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=10)
        
        title = ctk.CTkLabel(
            self.left_studio, text="💸 Central Expense Ledger",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color="#f38ba8"
        )
        title.pack(pady=15, padx=20, anchor="w")

        # Scrollable form container layout grid configuration
        self.form_scroll = ctk.CTkScrollableFrame(self.left_studio, fg_color="transparent")
        self.form_scroll.pack(fill="both", expand=True, padx=15, pady=5)
        self.form_scroll.grid_columnconfigure(1, weight=1)

        # Row 0: Expense Classification Dropdown
        self.create_form_label(self.form_scroll, "Expense Classification:", 0, 0)
        self.combo_classification = ctk.CTkComboBox(self.form_scroll, values=EXPENSE_TYPES, variable=self.expense_type, width=240, fg_color="#1e1e2e", dropdown_fg_color="#1e1e2e")
        self.combo_classification.grid(row=0, column=1, padx=10, pady=8, sticky="w")

        # Row 1: Net Outlay Cost Entry Field
        self.create_form_label(self.form_scroll, "Amount (PKR):", 1, 0)
        self.ent_amount = ctk.CTkEntry(self.form_scroll, textvariable=self.amount, width=240, fg_color="#1e1e2e")
        self.ent_amount.grid(row=1, column=1, padx=10, pady=8, sticky="w")

        # Row 2: Date Selector Calendar Control Node
        self.create_form_label(self.form_scroll, "Date of Expense:", 2, 0)
        self.cal_date = DateEntry(self.form_scroll, width=24, background="#313244", foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd")
        self.cal_date.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Row 3: Event Link Dropdown Mapping System
        self.create_form_label(self.form_scroll, "Link with Booking/Event:", 3, 0)
        self.combo_event = ctk.CTkComboBox(self.form_scroll, values=["None / General Expense"], variable=self.linked_event, width=240, fg_color="#1e1e2e", dropdown_fg_color="#1e1e2e")
        self.combo_event.grid(row=3, column=1, padx=10, pady=8, sticky="w")

        # Row 4: Liquid Settlement Method Selection
        self.create_form_label(self.form_scroll, "Payment Method:", 4, 0)
        self.combo_pay_method = ctk.CTkComboBox(self.form_scroll, values=PAYMENT_METHODS, variable=self.payment_method, width=240, fg_color="#1e1e2e", dropdown_fg_color="#1e1e2e")
        self.combo_pay_method.grid(row=4, column=1, padx=10, pady=8, sticky="w")

        # Row 5: Disbursed Authority Officer Signature Mapping
        self.create_form_label(self.form_scroll, "Paid Disbursed By:", 5, 0)
        self.ent_paid_by = ctk.CTkEntry(self.form_scroll, textvariable=self.paid_by, width=240, fg_color="#1e1e2e")
        self.ent_paid_by.grid(row=5, column=1, padx=10, pady=8, sticky="w")

        # Row 6: Reference ID Receipt Audits Token Codes
        self.create_form_label(self.form_scroll, "Reference / Receipt No:", 6, 0)
        self.ent_ref_no = ctk.CTkEntry(self.form_scroll, textvariable=self.reference_no, width=240, fg_color="#1e1e2e")
        self.ent_ref_no.grid(row=6, column=1, padx=10, pady=8, sticky="w")

        # Row 7: Settlement Status Options Box
        self.create_form_label(self.form_scroll, "Settlement Status:", 7, 0)
        self.combo_status = ctk.CTkComboBox(self.form_scroll, values=STATUS_TYPES, variable=self.status, width=240, fg_color="#1e1e2e", dropdown_fg_color="#1e1e2e")
        self.combo_status.grid(row=7, column=1, padx=10, pady=8, sticky="w")

        # Row 8: Bill/Slip Documents Storage Pipeline File Attachment
        self.create_form_label(self.form_scroll, "Upload Bill/Slip:", 8, 0)
        self.btn_file = ctk.CTkButton(self.form_scroll, text="📁 Attach Document", fg_color="#45475a", hover_color="#585b70", width=240, command=self.handle_file_attachment)
        self.btn_file.grid(row=8, column=1, padx=10, pady=8, sticky="w")

        # Row 9: Operational Narrative Annotations Block Text Frame
        self.create_form_label(self.form_scroll, "Operational Notes:", 9, 0)
        self.notes_text = ctk.CTkTextbox(self.form_scroll, width=240, height=80, fg_color="#1e1e2e", border_width=1, border_color="#45475a")
        self.notes_text.grid(row=9, column=1, padx=10, pady=8, sticky="w")

        # Generate Control Action Pipeline Command Dashboard Row
        self.render_action_buttons()

    def render_action_buttons(self):
        """Assembles interactive operational nodes inside workspace frame lower boundary."""
        btn_frame = ctk.CTkFrame(self.left_studio, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom", pady=20, padx=15)
        
        ctk.CTkButton(btn_frame, text="💾 Save Expense", fg_color="#f38ba8", text_color="#11111b", hover_color="#f2cdcd", width=110, font=("Segoe UI", 12, "bold"), command=self.save_expense_records).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="🔄 Update", fg_color="#f9e2af", text_color="#11111b", hover_color="#aba8f0", width=90, font=("Segoe UI", 12, "bold"), command=self.update_expense_records).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="🗑️ Delete", fg_color="#45475a", text_color="white", hover_color="#e78284", width=90, font=("Segoe UI", 12, "bold"), command=self.delete_expense_record).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="🧹 Clear", fg_color="#1e1e2e", text_color="white", hover_color="#313244", width=80, font=("Segoe UI", 12, "bold"), command=self.clear_form_fields).pack(side="right", padx=4)

    def setup_ui_layout_right(self):
        """
        Configures Right Workspace: System Integrated Ledger Dataview Board.
        Renders filter panels tools, builds modern treeview layouts objects.
        """
        self.right_ledger = ctk.CTkFrame(self, fg_color="#313244", corner_radius=15)
        self.right_ledger.grid(row=0, column=1, sticky="nsew", padx=(15, 0), pady=10)
        
        # Real-time Filter Matrix Management Unit Bar Elements
        filter_box = ctk.CTkFrame(self.right_ledger, fg_color="transparent")
        filter_box.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkEntry(filter_box, placeholder_text="🔍 Search Paid By or Ref...", textvariable=self.search_query, width=210, fg_color="#1e1e2e").pack(side="left", padx=(0, 10))
        
        type_filters = ["All Types"] + EXPENSE_TYPES
        ctk.CTkComboBox(filter_box, values=type_filters, variable=self.filter_type, width=170, fg_color="#1e1e2e", dropdown_fg_color="#1e1e2e", command=lambda e: self.refresh_table_data()).pack(side="left")
        
        ctk.CTkButton(filter_box, text="Filter Logs", fg_color="#b4befe", text_color="#11111b", hover_color="#89b4fa", font=("Segoe UI", 11, "bold"), width=90, command=self.refresh_table_data).pack(side="right", padx=5)
        
        # --------------------------------------------------------------------------
        # INTERACTIVE TREEVIEW RENDERING CONFIGURATION PIPELINE
        # --------------------------------------------------------------------------
        style = ttk.Style()
        style.configure("Treeview", background="#1e1e2e", fieldbackground="#1e1e2e", foreground="white", rowheight=28, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#11111b", foreground="#11111b", font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[("selected", "#f38ba8")], foreground=[("selected", "#11111b")])
        
        cols = ("ID", "Classification Type", "Amount", "Date", "Paid By", "Method", "Ref No", "Linked Event", "Status")
        self.ledger_table = ttk.Treeview(self.right_ledger, columns=cols, show="headings")
        
        widths = { "ID": 45, "Classification Type": 150, "Amount": 85, "Date": 90, "Paid By": 95, "Method": 80, "Ref No": 85, "Linked Event": 110, "Status": 75 }
        for c in cols:
            self.ledger_table.heading(c, text=c, anchor="w")
            self.ledger_table.column(c, width=widths.get(c, 90), anchor="w")
            
        scroll = ttk.Scrollbar(self.right_ledger, orient="vertical", command=self.ledger_table.yview)
        self.ledger_table.configure(yscrollcommand=scroll.set)
        
        scroll.pack(side="right", fill="y")
        self.ledger_table.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.ledger_table.bind("<<TreeviewSelect>>", self.on_record_row_selected)

    def create_form_label(self, parent, text, row, col):
        """Generates unified form tracking textual identifiers maps blocks."""
        lbl = ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#cdd6f4")
        lbl.grid(row=row, column=col, padx=15, pady=10, sticky="w")

    def handle_file_attachment(self):
        """Captures local files pointers properties maps elements onto buffer slots."""
        file = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png"), ("PDF Documents", "*.pdf")])
        if file:
            self.attachment_path = file
            self.btn_file.configure(text=f"✅ {os.path.basename(file)}", fg_color="#a6e3a1", text_color="#11111b")

    def load_active_events_dropdown(self):
        """Pulls ongoing confirmation entries rows records from remote bookings matrix tables."""
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, customer_name, event_date FROM bookings WHERE booking_status  != 'Cancelled' ORDER BY event_date DESC")
            self.event_map = {}
            dropdown_values = ["None / General Expense"]
            
            for eid, name, edate in cur.fetchall():
                display_str = f"ID: {eid} | {name} ({edate})"
                self.event_map[display_str] = eid
                dropdown_values.append(display_str)
                
            self.combo_event.configure(values=dropdown_values)
            conn.close()
        except Exception as query_fault:
            print(f"[Dropdown Hook Pipe Warning] Fail loading dynamic entries rows slots: {query_fault}")

    # ==========================================================================
    # DATA ARCHITECTURE RE-ENGINEERED PIPELINE ENGINE V3 (CRITICAL CORE)
    # ==========================================================================
    def refresh_table_data(self):
        """
        Pulls and dynamically merges direct manual input records with ALL external sub-khaatas.
        CRITICAL ARCHITECTURE: Fully prepared for future Employee/Staff salary module connection.
        Adding a new module ONLY requires expanding this SQL UNION ALL pipeline block mapping matrix.
        """
        if not hasattr(self, 'ledger_table'):
            self.setup_ui_layout_right()

        for row in self.ledger_table.get_children():
            self.ledger_table.delete(row)
            
        conn = connect_database()
        if not conn: return
        
        try:
            cur = conn.cursor()
            
            # --------------------------------------------------------------------------
            # CROSS-LINK PIPELINE ENGINE MATRIX (ENTERPRISE UNION ALL CLUSTER LOGIC)
            # --------------------------------------------------------------------------
            # Hum har sub-khaata se absolute columns extract kar ke unique schema signatures
            # generate kar rahay hain taake real-time data sync ho sakay.
            query = """
                SELECT id, expense_type, amount, expense_date, paid_by, payment_method, reference_no, 
                       CASE WHEN booking_id IS NULL THEN 'General' ELSE CONCAT('Booking #', booking_id) END as booking, status 
                FROM expenses WHERE 1=1
                
                UNION ALL
                
                SELECT id, 'Poultry (Chicken) Khaata' as expense_type, total_amount as amount, purchase_date as date, supplier_name as paid_by, 'Khaata Credit' as payment_method, CONCAT('Ch-ID: ', id) as reference_no,
                       CASE WHEN booking_id IS NULL THEN 'General Stock' ELSE CONCAT('Booking #', booking_id) END as booking, CASE WHEN remaining_balance <= 0 THEN 'Paid' ELSE 'Partial' END as status
                FROM khaata_chicken_poultry WHERE 1=1
                
                UNION ALL
                
                SELECT id, 'Meat (Mutton/Beef) Khaata' as expense_type, total_amount as amount, purchase_date as date, supplier_name as paid_by, 'Khaata Credit' as payment_method, CONCAT('Mt-ID: ', id) as reference_no,
                       CASE WHEN booking_id IS NULL THEN 'General Stock' ELSE CONCAT('Booking #', booking_id) END as booking, CASE WHEN remaining_balance <= 0 THEN 'Paid' ELSE 'Partial' END as status
                FROM khaata_mutton_beef WHERE 1=1
                
                UNION ALL
                
                SELECT id, 'Dairy & Milk Khaata' as expense_type, total_amount as amount, purchase_date as date, supplier_name as paid_by, 'Khaata Credit' as payment_method, CONCAT('Dy-ID: ', id) as reference_no,
                       CASE WHEN booking_id IS NULL THEN 'General Stock' ELSE CONCAT('Booking #', booking_id) END as booking, CASE WHEN remaining_balance <= 0 THEN 'Paid' ELSE 'Partial' END as status
                FROM khaata_milk_dairy WHERE 1=1
                
                UNION ALL
                
                SELECT id, 'Karyana Inventory' as expense_type, total_amount as amount, purchase_date as date, supplier_name as paid_by, 'Khaata Credit' as payment_method, CONCAT('Kr-ID: ', id) as reference_no,
                       CASE WHEN booking_id IS NULL THEN 'General Stock' ELSE CONCAT('Booking #', booking_id) END as booking, CASE WHEN remaining_balance <= 0 THEN 'Paid' ELSE 'Partial' END as status
                FROM khaata_karyana WHERE 1=1

                UNION ALL
                
                SELECT id, 'Cold Drinks Khaata' as expense_type, total_amount as amount, purchase_date as date, supplier_name as paid_by, 'Khaata Credit' as payment_method, CONCAT('CD-ID: ', id) as reference_no,
                       CASE WHEN booking_id IS NULL THEN 'General Stock' ELSE CONCAT('Booking #', booking_id) END as booking, CASE WHEN remaining_balance <= 0 THEN 'Paid' ELSE 'Partial' END as status
                FROM khaata_cold_drinks WHERE 1=1

                UNION ALL
                
                SELECT id, 'Fruits & Vegetables Khaata' as expense_type, total_amount as amount, purchase_date as date, supplier_name as paid_by, 'Khaata Credit' as payment_method, CONCAT('FV-ID: ', id) as reference_no,
                       CASE WHEN booking_id IS NULL THEN 'General Stock' ELSE CONCAT('Booking #', booking_id) END as booking, CASE WHEN remaining_balance <= 0 THEN 'Paid' ELSE 'Partial' END as status
                FROM khaata_fruits_vegs WHERE 1=1
                
                /* =========================================================================
                   FUTURE EXTENSION PLUGHOLE: STAFF SALARY MODULE CONNECTIVITY REFERENCE
                   =========================================================================
                   Jab aap agla 'Employee Management Module' create karenge, to aapko is 
                   expense core module file ko bilkul touch ya alter nahi karna parega.
                   Aap sirf niche diye gaye design template ke mutabiq database mein table 
                   banayenge aur UNION ALL pipeline use attach kar lega:
                   
                   UNION ALL
                   
                   SELECT id, 'Staff Salary' as expense_type, net_paid as amount, payment_date as date, staff_name as paid_by, payment_mode as payment_method, CONCAT('EMP-ID: ', employee_id) as reference_no,
                          'General Management' as booking, 'Paid' as status
                   FROM employee_salaries WHERE 1=1
                */
            """
            
            wrapped_query = f"SELECT * FROM ({query}) as integrated_ledger WHERE 1=1"
            params = []
            
            search = self.search_query.get().strip()
            if search:
                wrapped_query += " AND (paid_by LIKE %s OR reference_no LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])
                
            ftype = self.filter_type.get()
            if ftype != "All Types":
                wrapped_query += " AND expense_type = %s"
                params.append(ftype)
                
            wrapped_query += " ORDER BY expense_date DESC"
            cur.execute(wrapped_query, params)
            
            for row in cur.fetchall():
                status_curr = row[8].lower() if row[8] else "paid"
                self.ledger_table.insert("", "end", values=row, tags=(status_curr,))
                
            self.ledger_table.tag_configure("paid", background="#2a3b2b", foreground="#a6e3a1")
            self.ledger_table.tag_configure("pending", background="#3b2a2a", foreground="#f38ba8")
            self.ledger_table.tag_configure("partial", background="#3b3b2a", foreground="#f9e2af")
            
            conn.close()
        except Exception as query_fault:
            # Dropback protective matrix to ensure operation even if secondary tables are yet to be migrated
            print(f"[SQL Matrix Engine Trace Warning] Falling back to core structures queries: {query_fault}")
            self.load_safe_fallback_core_expenses(search, ftype)

    def load_safe_fallback_core_expenses(self, search, ftype):
        """Secures functional capability even if secondary sub-khaata system dependencies fail."""
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            query = "SELECT id, expense_type, amount, expense_date, paid_by, payment_method, reference_no, booking_id, status FROM expenses WHERE 1=1"
            params = []
            if search:
                query += " AND (paid_by LIKE %s OR reference_no LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])
            if ftype != "All Types":
                query += " AND expense_type = %s"
                params.append(ftype)
            query += " ORDER BY expense_date DESC"
            cur.execute(query, params)
            for row in cur.fetchall():
                self.ledger_table.insert("", "end", values=row, tags=(row[8].lower() if row[8] else "paid",))
            conn.close()
        except Exception as fallback_error:
            print(f"[Fallback Pipeline Crash] Critical error tracing master arrays elements: {fallback_error}")

    def save_expense_records(self):
        """Processes data checks, maps variables data bounds onto main core storage row structures."""
        if float(self.amount.get() or 0) <= 0:
            messagebox.showwarning("Validation Error", "Please declare a valid transactional amount.")
            return
            
        # Protect Automated Modules from Getting Overwritten Directly via Core Interface Input Slots
        # Yeh rule hamare manual entries system ko dynamic sub-khaatas aur future salary entries se secure rakhta hai.
        if "Khaata" in self.expense_type.get() or "Inventory" in self.expense_type.get() or self.expense_type.get() == "Staff Salary":
            if self.expense_type.get() == "Staff Salary":
                msg = "Staff Salary processing must be handled via the upcoming Employee Management Module.\nDirect insertion block active."
            else:
                msg = "Automated sub-khaata stock inventory entries cannot be directly declared from this control panel.\nPlease use their respective specialized data entry frames."
            messagebox.showerror("Permission Blocked", msg)
            return

        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            query = """INSERT INTO expenses 
                (expense_type, amount, expense_date, payment_method, paid_by, reference_no, status, attachment_path, notes, booking_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
            selected_event_str = self.linked_event.get()
            booking_id = self.event_map.get(selected_event_str, None) if selected_event_str in self.event_map else None
            
            data = (
                self.expense_type.get(),
                float(self.amount.get() or 0),
                self.cal_date.get_date().strftime("%Y-%m-%d"),
                self.payment_method.get(),
                self.paid_by.get().strip(),
                self.reference_no.get().strip(),
                self.status.get(),
                self.attachment_path,
                self.notes_text.get("1.0", "end").strip(),
                booking_id
            )
            cur.execute(query, data)
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Transactional Expense Bound into Central Registry.")
            self.clear_form_fields()
            self.refresh_table_data()
            
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
        except Exception as e:
            messagebox.showerror("Pipeline Insertion Error", str(e))

    def update_expense_records(self):
        """Mutates manual entry coordinates elements within shared cluster matrices tables."""
        if not self.selected_expense_id:
            messagebox.showwarning("Selection Warning", "Please pin down a data row from the ledger board first.")
            return
            
        # Security Guardrails for Automation Blocks Mapping Layer References
        # Yeh dynamic shield future Employee module ko bhi automatically security data block provide karega.
        if "Khaata" in self.expense_type.get() or "Inventory" in self.expense_type.get() or self.expense_type.get() == "Staff Salary":
            messagebox.showerror("Permission Blocked", "Automated system integrated logs cannot be overwritten from this manual panel.\nPlease perform alterations inside their native modular layout frames.")
            return

        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            query = """UPDATE expenses SET 
                expense_type=%s, amount=%s, expense_date=%s, payment_method=%s, paid_by=%s, 
                reference_no=%s, status=%s, attachment_path=%s, notes=%s, booking_id=%s WHERE id=%s"""
                
            selected_event_str = self.linked_event.get()
            booking_id = self.event_map.get(selected_event_str, None) if selected_event_str in self.event_map else None
            
            data = (
                self.expense_type.get(),
                float(self.amount.get() or 0),
                self.cal_date.get_date().strftime("%Y-%m-%d"),
                self.payment_method.get(),
                self.paid_by.get().strip(),
                self.reference_no.get().strip(),
                self.status.get(),
                self.attachment_path,
                self.notes_text.get("1.0", "end").strip(),
                booking_id,
                self.selected_expense_id
            )
            cur.execute(query, data)
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Transaction ID {self.selected_expense_id} Data Up-to-date.")
            self.clear_form_fields()
            self.refresh_table_data()
            
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
        except Exception as e:
            messagebox.showerror("Pipeline Update Error", str(e))

    def delete_expense_record(self):
        """Cascades delete command vectors exclusively over direct manual input rows data slots."""
        if not self.selected_expense_id:
            messagebox.showwarning("Selection Error", "Please select a target log to drop.")
            return
            
        if "Khaata" in self.expense_type.get() or "Inventory" in self.expense_type.get() or self.expense_type.get() == "Staff Salary":
            messagebox.showerror("Permission Blocked", "Interconnected structural logs cannot be destroyed from this control panel.")
            return

        confirm = messagebox.askyesno("Critical Confirmation", "Are you confident you want to drop this expense record entry permanently?")
        if not confirm: return
        
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM expenses WHERE id = %s", (self.selected_expense_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("System Registry", "Log dropped securely.")
            self.clear_form_fields()
            self.refresh_table_data()
            
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
        except Exception as e:
            messagebox.showerror("Purge Error", str(e))

    def on_record_row_selected(self, event):
        """Traces active dataview row item selection array parameters back into sliders."""
        items = self.ledger_table.selection()
        if not items: return
        vals = self.ledger_table.item(items[0], "values")
        
        # Capture raw primary values pointers arrays keys maps
        self.selected_expense_id = vals[0]
        curr_type = vals[1]
        
        self.expense_type.set(curr_type)
        self.amount.set(vals[2])
        self.cal_date.set_date(vals[3])
        self.paid_by.set(vals[4])
        self.payment_method.set(vals[5])
        self.reference_no.set(vals[6])
        
        # Dynamic handling to reverse match event strings markers
        target_booking_lbl = vals[7]
        if "Booking #" in target_booking_lbl:
            raw_b_id = target_booking_lbl.replace("Booking #", "").strip()
            matched_str = "None / General Expense"
            for dropdown_txt, internal_id in self.event_map.items():
                if str(internal_id) == str(raw_b_id):
                    matched_str = dropdown_txt
                    break
            self.linked_event.set(matched_str)
        else:
            self.linked_event.set("None / General Expense")
            
        self.status.set(vals[8] if vals[8] else "Paid")

    def clear_form_fields(self):
        """Flushes storage buffer array states cleanly before starting new inputs."""
        self.selected_expense_id = None
        self.attachment_path = None
        self.amount.set("0")
        self.paid_by.set("")
        self.reference_no.set("")
        self.expense_type.set(EXPENSE_TYPES[0])
        self.payment_method.set(PAYMENT_METHODS[0])
        self.status.set(STATUS_TYPES[0])
        self.linked_event.set("None / General Expense")
        self.cal_date.set_date(date.today())
        self.notes_text.delete("1.0", "end")
        self.btn_file.configure(text="📁 Attach Document", fg_color="#45475a", text_color="white")