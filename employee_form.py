# -*- coding: utf-8 -*-
# Save as: forms/employee_form.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date
from db.connection import connect_database

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Enterprise Enums for Staffing Categories
ROLES_LIST = [
    "Manager / Admin", 
    "Security Guard", 
    "Cleaner / Sweeper", 
    "Head Cook (Thekedar)", 
    "BBQ Specialist (Thekedar)", 
    "Tandoor / Roti (Thekedar)", 
    "Dishwasher (Thekedar)",
    "General Helper"
]
EMP_TYPES = ["Permanent (Fixed Monthly)", "Contractual / Thekedar (Event Based)"]
PAYMENT_METHODS = ["Cash", "Bank Transfer", "JazzCash", "Easypaisa", "Cheque"]

class EmployeeForm(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        """
        Initializes the Core Employee & Contractual Staff Payroll Module.
        Built with deep database linking to the Central Expenses framework.
        """
        super().__init__(master, fg_color="#1e1e2e", **kwargs)
        self.master = master
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.selected_id = None
        self.booking_id_map = {}
        
        # Enforce exact database schemas before rendering UI
        self.ensure_database_schema_layers()
        
        # Initialize UI tracking variables with math listeners
        self.initialize_form_variables()
        
        # Build split-screen professional matrix layout
        self.setup_ui_components()
        
        # Load external data (Bookings for event-based Thekedars) & Table
        self.refresh_booking_dropdown_list()
        self.refresh_table_dataset()

    def ensure_database_schema_layers(self):
        """Creates or updates the table architecture for HR and Payroll management."""
        conn = connect_database()
        if not conn:
            return
        try:
            cur = conn.cursor()
            
            # Sub-Khaata mapping schema for Employees & Payroll
            cur.execute("""
                CREATE TABLE IF NOT EXISTS employee_payroll (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    employee_name VARCHAR(150) NOT NULL,
                    role VARCHAR(100) NOT NULL,
                    emp_type VARCHAR(100) NOT NULL,
                    salary_month_event VARCHAR(100) NOT NULL,
                    net_salary DECIMAL(10,2) NOT NULL,
                    advance_paid DECIMAL(10,2) DEFAULT 0.00,
                    balance_due DECIMAL(10,2) DEFAULT 0.00,
                    payment_date DATE NOT NULL,
                    payment_method VARCHAR(50) DEFAULT 'Cash',
                    reference_no VARCHAR(100) NULL,
                    booking_id INT DEFAULT NULL,
                    linked_expense_id INT DEFAULT NULL,
                    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL,
                    FOREIGN KEY (linked_expense_id) REFERENCES expenses(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            conn.commit()
            conn.close()
        except Exception as schema_fault:
            messagebox.showerror("Database Enforcer Crash", f"Could not build HR tables:\n{str(schema_fault)}")

    def initialize_form_variables(self):
        """Instantiates variable handles with live cross-calculation math listeners."""
        self.v_emp_name = tk.StringVar()
        self.v_role = tk.StringVar(value=ROLES_LIST[0])
        self.v_emp_type = tk.StringVar(value=EMP_TYPES[0])
        self.v_salary_month = tk.StringVar()
        
        self.v_net_salary = tk.StringVar(value="0")
        self.v_advance_paid = tk.StringVar(value="0")
        
        self.v_pay_method = tk.StringVar(value=PAYMENT_METHODS[0])
        self.v_ref_no = tk.StringVar()
        
        self.v_booking_selection = tk.StringVar(value="None / General Monthly Salary")
        
        # Real-time tracking output string for UI
        self.lbl_calc_balance = tk.StringVar(value="PKR 0.00")
        
        # Listeners for real-time math engine
        self.v_net_salary.trace_add("write", self.execute_live_payroll_math)
        self.v_advance_paid.trace_add("write", self.execute_live_payroll_math)
        
        self.search_query = tk.StringVar()
        self.search_query.trace_add("write", lambda *args: self.refresh_table_dataset())

    def execute_live_payroll_math(self, *args):
        """Processes balance math dynamically to avoid manual entry faults."""
        try:
            net = float(self.v_net_salary.get()) if self.v_net_salary.get().replace('.', '', 1).isdigit() else 0.0
            paid = float(self.v_advance_paid.get()) if self.v_advance_paid.get().replace('.', '', 1).isdigit() else 0.0
            balance = net - paid
            
            self.lbl_calc_balance.set(f"PKR {balance:,.2f}")
        except Exception:
            self.lbl_calc_balance.set("PKR 0.00")

    def setup_ui_components(self):
        """Draws the Catppuccin Mocha themed high-end split layout."""
        self.grid_columnconfigure(0, weight=4) # Left Input Panel
        self.grid_columnconfigure(1, weight=6) # Right Dataview Ledger Panel
        self.grid_rowconfigure(0, weight=1)
        
        # ======================================================================
        # LEFT STUDIO: EMPLOYEE PAYROLL INPUT MODULE
        # ======================================================================
        editor_frame = ctk.CTkFrame(self, fg_color="#313244", corner_radius=12)
        editor_frame.grid(row=0, column=0, padx=(0, 15), sticky="nsew")
        
        lbl_header = ctk.CTkLabel(
            editor_frame, text="🧑‍🤝‍🧑 Staff & Thekedar Payroll",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#cba6f7"
        )
        lbl_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        scroll_container = ctk.CTkScrollableFrame(editor_frame, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # 1. Employee / Thekedar Profile Identity
        ctk.CTkLabel(scroll_container, text="Employee / Thekedar Name:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5, pady=(4, 0))
        ctk.CTkEntry(scroll_container, textvariable=self.v_emp_name, placeholder_text="e.g., Ali Raza, Master Chef Bashir", fg_color="#1e1e2e", text_color="#cdd6f4", border_color="#45475a", height=32).pack(fill="x", padx=5, pady=2)
        
        # 2. Staffing Matrix Types & Roles Dropdowns
        roles_row = ctk.CTkFrame(scroll_container, fg_color="transparent")
        roles_row.pack(fill="x", pady=4)
        roles_row.grid_columnconfigure((0, 1), weight=1)
        
        r_block = ctk.CTkFrame(roles_row, fg_color="transparent")
        r_block.grid(row=0, column=0, padx=(0, 4), sticky="nsew")
        ctk.CTkLabel(r_block, text="Designation / Role:", text_color="#cdd6f4", font=("Segoe UI", 11)).pack(anchor="w", padx=5)
        ctk.CTkComboBox(r_block, variable=self.v_role, values=ROLES_LIST, fg_color="#1e1e2e", button_color="#45475a", dropdown_fg_color="#1e1e2e").pack(fill="x", pady=2)
        
        t_block = ctk.CTkFrame(roles_row, fg_color="transparent")
        t_block.grid(row=0, column=1, padx=(4, 0), sticky="nsew")
        ctk.CTkLabel(t_block, text="Employment Type:", text_color="#cdd6f4", font=("Segoe UI", 11)).pack(anchor="w", padx=5)
        ctk.CTkComboBox(t_block, variable=self.v_emp_type, values=EMP_TYPES, fg_color="#1e1e2e", button_color="#45475a", dropdown_fg_color="#1e1e2e").pack(fill="x", pady=2)

        # 3. Contextual Timeline (Month / Event)
        ctk.CTkLabel(scroll_container, text="Salary Month / Event Reference:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5, pady=(6, 0))
        ctk.CTkEntry(scroll_container, textvariable=self.v_salary_month, placeholder_text="e.g., Salary June 2026 OR Walima Event #10", fg_color="#1e1e2e", border_color="#45475a", height=32).pack(fill="x", padx=5, pady=2)

        # 4. Linking to Specific Booking (Crucial for Thekedars)
        ctk.CTkLabel(scroll_container, text="Link to Event Booking (For Contractual):", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5, pady=(6, 0))
        self.dropdown_bookings = ctk.CTkOptionMenu(
            scroll_container, variable=self.v_booking_selection,
            values="None / General Monthly Salary", fg_color="#1e1e2e", button_color="#45475a", dropdown_fg_color="#1e1e2e", text_color="#cdd6f4"
        )
        self.dropdown_bookings.pack(fill="x", padx=5, pady=2)

        # 5. Financial Inputs (Net Earned vs Cash Taken)
        fin_row = ctk.CTkFrame(scroll_container, fg_color="transparent")
        fin_row.pack(fill="x", pady=6)
        fin_row.grid_columnconfigure((0, 1), weight=1)
        
        net_block = ctk.CTkFrame(fin_row, fg_color="transparent")
        net_block.grid(row=0, column=0, padx=(0, 4), sticky="nsew")
        ctk.CTkLabel(net_block, text="Net Total Salary/Bill (PKR):", text_color="#cdd6f4", font=("Segoe UI", 11)).pack(anchor="w", padx=5)
        ctk.CTkEntry(net_block, textvariable=self.v_net_salary, fg_color="#1e1e2e", border_color="#45475a").pack(fill="x", pady=2)
        
        adv_block = ctk.CTkFrame(fin_row, fg_color="transparent")
        adv_block.grid(row=0, column=1, padx=(4, 0), sticky="nsew")
        ctk.CTkLabel(adv_block, text="Cash/Advance Paid Out (PKR):", text_color="#cdd6f4", font=("Segoe UI", 11)).pack(anchor="w", padx=5)
        ctk.CTkEntry(adv_block, textvariable=self.v_advance_paid, fg_color="#1e1e2e", border_color="#45475a").pack(fill="x", pady=2)

        # 6. Payment Metadata Pipeline
        meta_row = ctk.CTkFrame(scroll_container, fg_color="transparent")
        meta_row.pack(fill="x", pady=4)
        meta_row.grid_columnconfigure((0, 1), weight=1)
        
        m_block = ctk.CTkFrame(meta_row, fg_color="transparent")
        m_block.grid(row=0, column=0, padx=(0, 4), sticky="nsew")
        ctk.CTkLabel(m_block, text="Payment Method:", text_color="#cdd6f4", font=("Segoe UI", 11)).pack(anchor="w", padx=5)
        ctk.CTkComboBox(m_block, variable=self.v_pay_method, values=PAYMENT_METHODS, fg_color="#1e1e2e", button_color="#45475a").pack(fill="x", pady=2)
        
        ref_block = ctk.CTkFrame(meta_row, fg_color="transparent")
        ref_block.grid(row=0, column=1, padx=(4, 0), sticky="nsew")
        ctk.CTkLabel(ref_block, text="Bank/Transfer Ref No:", text_color="#cdd6f4", font=("Segoe UI", 11)).pack(anchor="w", padx=5)
        ctk.CTkEntry(ref_block, textvariable=self.v_ref_no, fg_color="#1e1e2e", border_color="#45475a").pack(fill="x", pady=2)

        # 7. Disbursed Date Tracking
        ctk.CTkLabel(scroll_container, text="Date of Log / Payment:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5, pady=(6, 0))
        self.dt_payment = DateEntry(scroll_container, width=16, background='#313244', foreground='#cdd6f4', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.dt_payment.pack(fill="x", padx=5, pady=4)

        # 8. Outstanding Balance Alert Card (Read Only)
        balance_card = ctk.CTkFrame(scroll_container, fg_color="#1e1e2e", corner_radius=8, border_width=1, border_color="#f38ba8")
        balance_card.pack(fill="x", pady=15, padx=5)
        
        ctk.CTkLabel(balance_card, text="Pending Balance / Arrears Due:", text_color="#a6adc8", font=("Segoe UI", 11, "bold")).pack(pady=(10, 0))
        ctk.CTkLabel(balance_card, textvariable=self.lbl_calc_balance, text_color="#f38ba8", font=("Segoe UI", 18, "bold")).pack(pady=(0, 10))

        # Core Action Trigger Control Buttons Array
        btn_layout_strip = ctk.CTkFrame(editor_frame, fg_color="transparent")
        btn_layout_strip.pack(fill="x", side="bottom", padx=15, pady=15)
        btn_layout_strip.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkButton(btn_layout_strip, text="Save Log", font=("Segoe UI", 12, "bold"), fg_color="#a6e3a1", text_color="#11111b", hover_color="#89b4fa", height=36, command=self.execute_save_payroll_pipeline).grid(row=0, column=0, padx=2, sticky="nsew")
        ctk.CTkButton(btn_layout_strip, text="Update Log", font=("Segoe UI", 12, "bold"), fg_color="#f9e2af", text_color="#11111b", hover_color="#89b4fa", height=36, command=self.execute_update_payroll_pipeline).grid(row=0, column=1, padx=2, sticky="nsew")
        ctk.CTkButton(btn_layout_strip, text="Delete", font=("Segoe UI", 12, "bold"), fg_color="#f38ba8", text_color="#11111b", hover_color="#89b4fa", height=36, command=self.execute_purge_payroll_pipeline).grid(row=0, column=2, padx=2, sticky="nsew")

        # ======================================================================
        # RIGHT STUDIO: EMPLOYEE PAYROLL HISTORY VIEWPORT
        # ======================================================================
        monitor_frame = ctk.CTkFrame(self, fg_color="#313244", corner_radius=12)
        monitor_frame.grid(row=0, column=1, sticky="nsew")
        
        top_bar = ctk.CTkFrame(monitor_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkEntry(top_bar, placeholder_text="🔍 Search Name...", textvariable=self.search_query, width=200, fg_color="#1e1e2e", border_color="#45475a").pack(side="left")
        
        ctk.CTkButton(top_bar, text="Export Sheet", font=("Segoe UI", 11, "bold"), fg_color="#89b4fa", text_color="#11111b", width=90, height=28, command=self.execute_excel_export_matrix).pack(side="right")
        
        # Native Styled OS Treeview Injection
        table_wrapper = ctk.CTkFrame(monitor_frame, fg_color="#1e1e2e", corner_radius=10)
        table_wrapper.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        style = ttk.Style()
        style.configure("Treeview", background="#1e1e2e", fieldbackground="#1e1e2e", foreground="#cdd6f4", rowheight=30, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#11111b", foreground="#11111b", font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[("selected", "#89b4fa")], foreground=[("selected", "#11111b")])
        
        cols = ("ID", "Staff Name", "Role", "Context", "Net Pay", "Paid Out", "Balance", "Date", "Status")
        self.ledger_table = ttk.Treeview(table_wrapper, columns=cols, show="headings")
        
        w_map = { "ID": 40, "Staff Name": 130, "Role": 110, "Context": 110, "Net Pay": 80, "Paid Out": 80, "Balance": 80, "Date": 85, "Status": 70 }
        for c in cols:
            self.ledger_table.heading(c, text=c, anchor="w")
            self.ledger_table.column(c, width=w_map.get(c, 80), anchor="w")
            
        scroll = ttk.Scrollbar(table_wrapper, orient="vertical", command=self.ledger_table.yview)
        self.ledger_table.configure(yscrollcommand=scroll.set)
        
        scroll.pack(side="right", fill="y")
        self.ledger_table.pack(fill="both", expand=True, padx=2, pady=2)
        self.ledger_table.bind("<<TreeviewSelect>>", self.on_record_row_selected)

    def refresh_booking_dropdown_list(self):
        """Fetches active events context keys so Thekedar cost can map cleanly to events."""
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, customer_name, event_date FROM bookings WHERE booking_status != 'Cancelled' ORDER BY event_date ASC")
            dataset = cur.fetchall()
            conn.close()
            
            options_pool = ["None / General Monthly Salary"]
            self.booking_id_map.clear()
            
            for b_id, name, ev_date in dataset:
                map_str = f"ID: {b_id} | {name} ({ev_date})"
                options_pool.append(map_str)
                self.booking_id_map[map_str] = b_id
                
            self.dropdown_bookings.configure(values=options_pool)
        except Exception as e:
            print(f"Dropdown Sync Fault: {e}")

    def refresh_table_dataset(self):
        """Pulls comprehensive payroll transactional vectors from native database clusters."""
        for row in self.ledger_table.get_children():
            self.ledger_table.delete(row)
            
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            sq = self.search_query.get().strip()
            
            sql = """
                SELECT id, employee_name, role, salary_month_event, net_salary, advance_paid, balance_due, payment_date,
                       CASE WHEN balance_due <= 0 THEN 'Cleared' ELSE 'Pending' END as status
                FROM employee_payroll
            """
            
            if sq:
                sql += " WHERE employee_name LIKE %s OR role LIKE %s ORDER BY payment_date DESC"
                cur.execute(sql, (f"%{sq}%", f"%{sq}%"))
            else:
                sql += " ORDER BY payment_date DESC"
                cur.execute(sql)
                
            for row in cur.fetchall():
                status_tag = "cleared" if row[8] == 'Cleared' else "pending"
                self.ledger_table.insert("", "end", values=row, tags=(status_tag,))
                
            self.ledger_table.tag_configure("cleared", foreground="#a6e3a1")
            self.ledger_table.tag_configure("pending", foreground="#f38ba8")
            
            conn.close()
        except Exception as e:
            messagebox.showerror("SQL Core Fault", f"Could not sync arrays:\n{str(e)}")

    def on_record_row_selected(self, event):
        """Re-binds selected layout lines directly onto control widgets mappings."""
        items = self.ledger_table.selection()
        if not items: return
        
        row_id = self.ledger_table.item(items[0], "values")[0]
        self.selected_id = row_id
        
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT employee_name, role, emp_type, salary_month_event, net_salary, advance_paid, 
                       payment_date, payment_method, reference_no, booking_id
                FROM employee_payroll WHERE id = %s
            """, (row_id,))
            res = cur.fetchone()
            conn.close()
            
            if res:
                self.v_emp_name.set(res[0])
                self.v_role.set(res[1])
                self.v_emp_type.set(res[2])
                self.v_salary_month.set(res[3])
                self.v_net_salary.set(str(res[4]))
                self.v_advance_paid.set(str(res[5]))
                self.dt_payment.set_date(res[6])
                self.v_pay_method.set(res[7])
                self.v_ref_no.set(res[8] if res[8] else "")
                
                # Restore Reverse Engineering Context Drops Hooks
                b_id = res[9]
                matched_str = "None / General Monthly Salary"
                if b_id:
                    for txt, int_id in self.booking_id_map.items():
                        if str(int_id) == str(b_id):
                            matched_str = txt
                            break
                self.v_booking_selection.set(matched_str)
                
                # Re-trigger calculation
                self.execute_live_payroll_math()
        except Exception as e:
            messagebox.showerror("Selection Bind Error", str(e))

    def execute_save_payroll_pipeline(self):
        """Safely commits staff expenditures into HR schemas AND Central Expense Ledgers."""
        if not self.v_emp_name.get().strip() or not self.v_salary_month.get().strip():
            messagebox.showwarning("Validation Constraint", "Employee Identity and Month/Event reference cannot be empty.")
            return
            
        try:
            net = float(self.v_net_salary.get())
            paid = float(self.v_advance_paid.get())
            balance = net - paid
        except ValueError:
            messagebox.showerror("Numerical Constraint", "Financial attributes must be numerical configurations.")
            return
            
        bk_str = self.v_booking_selection.get()
        target_booking = self.booking_id_map.get(bk_str, None)
        
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            
            # --- 1. DOUBLE ENTRY SYNC TO CORE EXPENSES ---
            # Total net_salary accrues to expenses to ensure Net Profit is exact. Liquid cash is implicitly traced via sub-layer.
            status_flag = "Paid" if balance <= 0 else ("Partial" if paid > 0 else "Pending")
            exp_desc = f"Staff Payroll: {self.v_emp_name.get()} ({self.v_role.get()}) - Context: {self.v_salary_month.get()}"
            
            cur.execute("""
                INSERT INTO expenses (
                    expense_type, amount, expense_date, paid_by, payment_method, reference_no, status, notes, booking_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                "Staff Salary", net, self.dt_payment.get_date(), "Marquee Office", self.v_pay_method.get(),
                self.v_ref_no.get(), status_flag, exp_desc, target_booking
            ))
            gen_exp_id = cur.lastrowid
            
            # --- 2. ISOLATED HR SUB-LEDGER COMMIT ---
            cur.execute("""
                INSERT INTO employee_payroll (
                    employee_name, role, emp_type, salary_month_event, net_salary, advance_paid,
                    balance_due, payment_date, payment_method, reference_no, booking_id, linked_expense_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.v_emp_name.get().strip(), self.v_role.get(), self.v_emp_type.get(),
                self.v_salary_month.get().strip(), net, paid, balance, self.dt_payment.get_date(),
                self.v_pay_method.get(), self.v_ref_no.get(), target_booking, gen_exp_id
            ))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Pipeline Success", "Staff Payroll logged and synchronized natively to core expenses.")
            self.clear_form_fields()
            self.refresh_table_dataset()
            
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
        except Exception as e:
            messagebox.showerror("Execution Framework Halt", str(e))

    def execute_update_payroll_pipeline(self):
        """Rewrites and synchronizes states across Employee sub-structures and Central routes."""
        if not self.selected_id:
            messagebox.showwarning("Target Drop", "Select an element to execute an update rewrite.")
            return
            
        try:
            net = float(self.v_net_salary.get())
            paid = float(self.v_advance_paid.get())
            balance = net - paid
        except ValueError:
            messagebox.showerror("Constraint Alert", "Amounts must remain numeric standard coordinates.")
            return

        bk_str = self.v_booking_selection.get()
        target_booking = self.booking_id_map.get(bk_str, None)
        
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            
            # Fetch mapped expense cross-link
            cur.execute("SELECT linked_expense_id FROM employee_payroll WHERE id = %s", (self.selected_id,))
            link_record = cur.fetchone()
            
            status_flag = "Paid" if balance <= 0 else ("Partial" if paid > 0 else "Pending")
            exp_desc = f"Staff Payroll: {self.v_emp_name.get()} ({self.v_role.get()}) - Context: {self.v_salary_month.get()}"
            
            if link_record and link_record[0]:
                cur.execute("""
                    UPDATE expenses SET amount=%s, expense_date=%s, payment_method=%s, reference_no=%s, status=%s, notes=%s, booking_id=%s
                    WHERE id=%s
                """, (net, self.dt_payment.get_date(), self.v_pay_method.get(), self.v_ref_no.get(), status_flag, exp_desc, target_booking, link_record[0]))
                
            cur.execute("""
                UPDATE employee_payroll SET
                    employee_name=%s, role=%s, emp_type=%s, salary_month_event=%s, net_salary=%s, advance_paid=%s,
                    balance_due=%s, payment_date=%s, payment_method=%s, reference_no=%s, booking_id=%s
                WHERE id=%s
            """, (
                self.v_emp_name.get().strip(), self.v_role.get(), self.v_emp_type.get(), self.v_salary_month.get().strip(),
                net, paid, balance, self.dt_payment.get_date(), self.v_pay_method.get(), self.v_ref_no.get(), target_booking, self.selected_id
            ))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Mutations Verified", "Data coordinates merged securely.")
            self.clear_form_fields()
            self.refresh_table_dataset()
            
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
        except Exception as e:
            messagebox.showerror("Update Framework Alert", str(e))

    def execute_purge_payroll_pipeline(self):
        """Drops operational records perfectly preventing orphan keys traces."""
        if not self.selected_id:
            return
            
        verify = messagebox.askyesno("Secure Protocol Alert", "Confirm dropping employee payroll ledger history forever?")
        if not verify: return
        
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("SELECT linked_expense_id FROM employee_payroll WHERE id = %s", (self.selected_id,))
            link = cur.fetchone()
            
            cur.execute("DELETE FROM employee_payroll WHERE id = %s", (self.selected_id,))
            if link and link[0]:
                cur.execute("DELETE FROM expenses WHERE id = %s", (link[0],))
                
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Purge OK", "Data coordinates evaporated.")
            self.clear_form_fields()
            self.refresh_table_dataset()
            
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
        except Exception as e:
            messagebox.showerror("Engine Fault", str(e))

    def clear_form_fields(self):
        self.selected_id = None
        self.v_emp_name.set("")
        self.v_role.set(ROLES_LIST[0])
        self.v_emp_type.set(EMP_TYPES[0])
        self.v_salary_month.set("")
        self.v_net_salary.set("0")
        self.v_advance_paid.set("0")
        self.dt_payment.set_date(date.today())
        self.v_pay_method.set(PAYMENT_METHODS[0])
        self.v_ref_no.set("")
        self.v_booking_selection.set("None / General Monthly Salary")
        self.lbl_calc_balance.set("PKR 0.00")

    def execute_excel_export_matrix(self):
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM employee_payroll ORDER BY payment_date DESC")
            data = cur.fetchall()
            cols = [desc[0] for desc in cur.description]
            conn.close()
            
            p = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx"),("CSV", "*.csv")])
            if not p: return
            
            if p.endswith(".xlsx") and PANDAS_AVAILABLE:
                pd.DataFrame(data, columns=cols).to_excel(p, index=False)
            else:
                import csv
                with open(p, "w", newline='', encoding='utf-8') as f:
                    w = csv.writer(f)
                    w.writerow(cols)
                    w.writerows(data)
            messagebox.showinfo("Export Exported", "Matrix dropped strictly to disk.")
        except Exception as e:
            messagebox.showerror("IO Fault", str(e))