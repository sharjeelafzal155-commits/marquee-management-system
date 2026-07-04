# -*- coding: utf-8 -*-
# Save as: forms/reports.py

import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date, datetime
from db.connection import connect_database

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class ReportsScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        # Premium Dark Palette Configuration Matrix Matching Executive Dashboard
        super().__init__(master, fg_color="#1e1e2e", **kwargs)
        self.master = master
        
        # UI Metrics Analytics Variables
        self.total_revenue_var = tk.StringVar(value="PKR 0.00")
        self.total_expense_var = tk.StringVar(value="PKR 0.00")
        self.net_profit_loss_var = tk.StringVar(value="PKR 0.00")
        
        # Construct Screen Layout Components Securely
        self.setup_ui_components()
        
        # Trigger default data pull for the current month window
        self.execute_financial_audit()

    def setup_ui_components(self):
        """Builds the complete analytical engine dashboard view matching premium UI specs."""
        # --- Top Header Controller ---
        header_frame = ctk.CTkFrame(self, fg_color="#181825", height=60, corner_radius=8)
        header_frame.pack(fill="x", padx=15, pady=10)
        header_frame.pack_propagate(False)
        
        lbl_title = ctk.CTkLabel(header_frame, text="FINANCIAL AUDIT & REPORTING ENGINE", 
                                 font=ctk.CTkFont(family="Consolas", size=16, weight="bold"), 
                                 text_color="#cba6f7")
        lbl_title.pack(side="left", padx=15, pady=15)
        
        # --- Filter Control Panel ---
        filter_frame = ctk.CTkFrame(self, fg_color="#313244", corner_radius=8)
        filter_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(filter_frame, text="Start Date:", text_color="#cdd6f4").grid(row=0, column=0, padx=10, pady=15, sticky="w")
        self.dt_start = DateEntry(filter_frame, width=12, background='#cba6f7', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        # Set to 1st of current month dynamically
        self.dt_start.set_date(date.today().replace(day=1))
        self.dt_start.grid(row=0, column=1, padx=5, pady=15)
        
        ctk.CTkLabel(filter_frame, text="End Date:", text_color="#cdd6f4").grid(row=0, column=2, padx=10, pady=15, sticky="w")
        self.dt_end = DateEntry(filter_frame, width=12, background='#cba6f7', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.dt_end.grid(row=0, column=3, padx=5, pady=15)
        
        btn_calculate = ctk.CTkButton(filter_frame, text="Run Final Calculation", fg_color="#cba6f7", hover_color="#b4befe",
                                      text_color="#11111b", font=ctk.CTkFont(weight="bold"), command=self.execute_financial_audit)
        btn_calculate.grid(row=0, column=4, padx=20, pady=15)
        
        btn_export = ctk.CTkButton(filter_frame, text="Export Statement (Excel)", fg_color="#a6e3a1", hover_color="#94e2d5",
                                   text_color="#11111b", font=ctk.CTkFont(weight="bold"), command=self.export_excel_report)
        btn_export.grid(row=0, column=5, padx=10, pady=15)

        # --- Executive Summary Cards (Big Numbers Real-Time Updates) ---
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=15, pady=10)
        cards_frame.columnconfigure((0, 1, 2), weight=1, uniform="equal")
        
        # Card 1: Total Gross Sales / Revenue Matrix Container
        card_rev = ctk.CTkFrame(cards_frame, fg_color="#313244", corner_radius=8, border_width=1, border_color="#a6e3a1")
        card_rev.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card_rev, text="TOTAL GROSS REVENUE (SALES)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a6adc8").pack(pady=(10,0))
        self.lbl_rev_num = ctk.CTkLabel(card_rev, textvariable=self.total_revenue_var, font=ctk.CTkFont(family="Consolas", size=22, weight="bold"), text_color="#a6e3a1")
        self.lbl_rev_num.pack(pady=10)
        
        # Card 2: Total Expenses Outflow Container
        card_exp = ctk.CTkFrame(cards_frame, fg_color="#313244", corner_radius=8, border_width=1, border_color="#f38ba8")
        card_exp.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(card_exp, text="TOTAL EXPENSES OUTFLOW", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a6adc8").pack(pady=(10,0))
        self.lbl_exp_num = ctk.CTkLabel(card_exp, textvariable=self.total_expense_var, font=ctk.CTkFont(family="Consolas", size=22, weight="bold"), text_color="#f38ba8")
        self.lbl_exp_num.pack(pady=10)
        
        # Card 3: Net Profit / Loss Reactive Status Card
        self.card_net = ctk.CTkFrame(cards_frame, fg_color="#313244", corner_radius=8, border_width=2, border_color="#cba6f7")
        self.card_net.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        self.lbl_net_title = ctk.CTkLabel(self.card_net, text="NET BUSINESS SYSTEM STATE: EVALUATING", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a6adc8")
        self.lbl_net_title.pack(pady=(10,0))
        self.lbl_net_num = ctk.CTkLabel(self.card_net, textvariable=self.net_profit_loss_var, font=ctk.CTkFont(family="Consolas", size=24, weight="bold"), text_color="#cba6f7")
        self.lbl_net_num.pack(pady=10)

        # --- Detailed Breakdown Section ---
        breakdown_frame = ctk.CTkFrame(self, fg_color="#181825", corner_radius=8)
        breakdown_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        lbl_breakdown_title = ctk.CTkLabel(breakdown_frame, text="Itemized Cost Distribution Breakdown Ledger", 
                                           font=ctk.CTkFont(weight="bold"), text_color="#a6adc8")
        lbl_breakdown_title.pack(anchor="w", padx=15, pady=10)
        
        # Scrollable console-like container for clean breakdown lists
        self.text_container = ctk.CTkTextbox(breakdown_frame, fg_color="#1e1e2e", font=ctk.CTkFont(family="Consolas", size=13), text_color="#cdd6f4")
        self.text_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.text_container.configure(state="disabled")

    def execute_financial_audit(self):
        """Performs exact mathematical double-entry audits across all operational databases pipelines."""
        start_d = self.dt_start.get_date().strftime('%Y-%m-%d')
        end_d = self.dt_end.get_date().strftime('%Y-%m-%d')
        
        conn = connect_database()
        if not conn:
            messagebox.showerror("Database Connection Error", "Could not establish safe pipeline to database cluster.")
            return
            
        try:
            cur = conn.cursor()
            
            # FIXED QUERY: total_amount ko direct sum kar rahe hain bina kisi complex filter ke jo dashboard pe chal raha hai
            rev_query = """
                SELECT COALESCE(SUM(total_amount), 0) 
                FROM bookings 
                WHERE booking_date BETWEEN %s AND %s
            """
            cur.execute(rev_query, (start_d, end_d))
            gross_revenue = float(cur.fetchone()[0])
            
            # Calculate Central Expenses Breakdown dynamically categorized from expenses table
            exp_query = """
                SELECT expense_type, COALESCE(SUM(amount), 0) 
                FROM expenses 
                WHERE expense_date BETWEEN %s AND %s
                GROUP BY expense_type
            """
            cur.execute(exp_query, (start_d, end_d))
            expense_rows = cur.fetchall()
            
            conn.close()
            
            # Build Category Dictionary mapping for professional text ledger output
            expense_map = {row[0]: float(row[1]) for row in expense_rows}
            total_expenses = sum(expense_map.values())
            
            # Final Profit / Loss Target Formula Logic Execution
            net_delta = gross_revenue - total_expenses
            
            # Reactive UI Framework Value Matrix Updates
            self.total_revenue_var.set(f"PKR {gross_revenue:,.2f}")
            self.total_expense_var.set(f"PKR {total_expenses:,.2f}")
            self.net_profit_loss_var.set(f"PKR {net_delta:,.2f}")
            
            # Dynamic Card Borders Refactoring based on validation rules
            if net_delta >= 0:
                self.card_net.configure(border_color="#a6e3a1") # Elegant Green for Surplus Profit
                self.lbl_net_num.configure(text_color="#a6e3a1")
                self.lbl_net_title.configure(text="NET BUSINESS SYSTEM STATE: PROFIT")
            else:
                self.card_net.configure(border_color="#f38ba8") # Urgent Red Border for Deficit Loss
                self.lbl_net_num.configure(text_color="#f38ba8")
                self.lbl_net_title.configure(text="NET BUSINESS SYSTEM STATE: CRITICAL LOSS")
                
            # Render Clean Text Summary Audit Trail directly inside UI console box
            self.render_ledger_view(start_d, end_d, gross_revenue, total_expenses, net_delta, expense_map)
            
        except Exception as audit_fault:
            if conn: conn.close()
            messagebox.showerror("Audit Engine Interrupted", f"Failed to compute final financial matrices:\n{str(audit_fault)}")

    def render_ledger_view(self, start_d, end_d, rev, exp, net, exp_map):
        """Prints a completely professional clean audit trail log into the screen textbox wrapper."""
        self.text_container.configure(state="normal")
        self.text_container.delete("1.0", "end")
        
        divider = "=" * 70 + "\n"
        sub_divider = "-" * 70 + "\n"
        
        ledger_text = ""
        ledger_text += divider
        ledger_text += f" FINANCIAL ACCOUNT STATEMENT MATRIX LAYER: {start_d} TO {end_d}\n"
        ledger_text += divider
        ledger_text += f" [+] TOTAL INCOMING REVENUE PIPELINE (BOOKINGS) : PKR {rev:,.2f}\n"
        ledger_text += divider
        ledger_text += " CATEGORY-WISE OPERATIONAL OUTFLOW BREAKDOWN:\n"
        ledger_text += sub_divider
        
        # Absolute routing logic to handle dynamic forms directory structure without module exceptions
        try:
            from forms.expense_form import EXPENSE_TYPES
        except ModuleNotFoundError:
            try:
                from expense_form import EXPENSE_TYPES
            except ImportError:
                EXPENSE_TYPES = ["Utilities (Electricity/Gas)", "Staff Salary", "Maintenance & Repairs", "Poultry (Chicken) Khaata", "Meat (Mutton/Beef) Khaata", "Dairy & Milk Khaata", "Karyana Inventory", "Cold Drinks Khaata", "Fruits & Vegetables Khaata", "Marketing", "Misc"]

        for cat in EXPENSE_TYPES:
            amt = exp_map.get(cat, 0.0)
            ledger_text += f"   > {cat:<35} : PKR {amt:,.2f}\n"
            
        ledger_text += sub_divider
        ledger_text += f" [-] TOTAL CASH EXPENSES CONSOLIDATED MARGIN   : PKR {exp:,.2f}\n"
        ledger_text += divider
        
        if net >= 0:
            ledger_text += f" [SUCCESS] SURPLUS NET PROFIT YIELD TO VAULT    : PKR {net:,.2f}\n"
        else:
            ledger_text += f" [CRITICAL] DEFICIT NET LOSS MARGIN DETECTED    : PKR {abs(net):,.2f}\n"
        ledger_text += divider
        
        self.text_container.insert("1.0", ledger_text)
        self.text_container.configure(state="disabled")

    def export_excel_report(self):
        """Serializes current query window data to clean localized production Excel spreadsheets."""
        if not PANDAS_AVAILABLE:
            messagebox.showerror("Dependency Missing", "Pandas toolkit engine library is not installed inside host environment.")
            return
            
        start_d = self.dt_start.get_date().strftime('%Y-%m-%d')
        end_d = self.dt_end.get_date().strftime('%Y-%m-%d')
        
        conn = connect_database()
        if not conn: return
        
        try:
            cur = conn.cursor()
            query = """
                SELECT id AS 'Expense ID', expense_type AS 'Expense Type', amount AS 'Amount (PKR)', 
                       expense_date AS 'Expense Date', paid_by AS 'Paid By', payment_method AS 'Payment Method', 
                       reference_no AS 'Reference No', booking_id AS 'Linked Booking ID', status AS 'Payment Status'
                FROM expenses 
                WHERE expense_date BETWEEN %s AND %s 
                ORDER BY expense_date DESC
            """
            cur.execute(query, (start_d, end_d))
            raw_dataset = cur.fetchall()
            headers = [desc[0] for desc in cur.description]
            conn.close()
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Matrix Sheet", "*.xlsx"), ("Flat CSV Sheet Stream", "*.csv")]
            )
            if not save_path: return
            
            df = pd.DataFrame(raw_dataset, columns=headers)
            
            if save_path.endswith(".csv"):
                df.to_csv(save_path, index=False, encoding='utf-8')
            else:
                df.to_excel(save_path, index=False)
                
            messagebox.showinfo("Export Master", f"✅ Production sheet metrics archived cleanly at:\n{save_path}")
        except Exception as export_fault:
            if conn: conn.close()
            messagebox.showerror("Export Interrupted", str(export_fault))