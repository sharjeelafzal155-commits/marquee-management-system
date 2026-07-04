# -*- coding: utf-8 -*
# Save as: forms/owner_share_summary.py

import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date
from db.connection import connect_database

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class OwnerShareSummaryScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        # Premium Modern Dark Palette Matrix (Catppuccin Mocha Base)
        super().__init__(master, fg_color="#1e1e2e", **kwargs)
        self.master = master
        
        # Reactive State Variables Initialization for Live Audit
        self.raw_profit_var = tk.StringVar(value="PKR 0.00")
        self.charity_var = tk.StringVar(value="PKR 0.00")
        self.distributable_var = tk.StringVar(value="PKR 0.00")
        
        # Owners Specific Equity Allocation Variables
        self.share_afzal_var = tk.StringVar(value="PKR 0.00")
        self.share_nadir_var = tk.StringVar(value="PKR 0.00")
        self.share_hayat_var = tk.StringVar(value="PKR 0.00")
        
        # Build High-End UI Layout Matrix Components
        self.setup_ui_layout()
        
        # Bootstrapping Default Ledger Audit Execution for Current Month
        self.calculate_equity_distribution()

    def setup_ui_layout(self):
        """Constructs the administrative layout frame nodes inside host canvas."""
        # --- Upper Branding Control Header ---
        header_frame = ctk.CTkFrame(self, fg_color="#181825", height=65, corner_radius=10)
        header_frame.pack(fill="x", padx=15, pady=12)
        header_frame.pack_propagate(False)
        
        lbl_title = ctk.CTkLabel(header_frame, text="OWNERS EQUITY SHARE & CHARITY DISTRIBUTION ENGINE", 
                                 font=ctk.CTkFont(family="Consolas", size=15, weight="bold"), 
                                 text_color="#f5c2e7")
        lbl_title.pack(side="left", padx=15, pady=18)
        
        # --- Chrono Control Range Filter Panel ---
        filter_frame = ctk.CTkFrame(self, fg_color="#313244", corner_radius=10)
        filter_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(filter_frame, text="From Date:", text_color="#cdd6f4", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=12, pady=15, sticky="w")
        self.dt_start = DateEntry(filter_frame, width=12, background='#f5c2e7', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.dt_start.set_date(date.today().replace(day=1)) # Default to first day of current month
        self.dt_start.grid(row=0, column=1, padx=5, pady=15)
        
        ctk.CTkLabel(filter_frame, text="To Date:", text_color="#cdd6f4", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=12, pady=15, sticky="w")
        self.dt_end = DateEntry(filter_frame, width=12, background='#f5c2e7', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.dt_end.grid(row=0, column=3, padx=5, pady=15)
        
        btn_run = ctk.CTkButton(filter_frame, text="Compute Distributions", fg_color="#f5c2e7", hover_color="#b4befe",
                                 text_color="#11111b", font=ctk.CTkFont(weight="bold"), command=self.calculate_equity_distribution)
        btn_run.grid(row=0, column=4, padx=25, pady=15)
        
        btn_export = ctk.CTkButton(filter_frame, text="Export Share Ledger", fg_color="#a6e3a1", hover_color="#94e2d5",
                                   text_color="#11111b", font=ctk.CTkFont(weight="bold"), command=self.export_distribution_matrix)
        btn_export.grid(row=0, column=5, padx=5, pady=15)

        # --- Top Executive Summary Row (The Master Pool) ---
        pool_frame = ctk.CTkFrame(self, fg_color="transparent")
        pool_frame.pack(fill="x", padx=15, pady=10)
        pool_frame.columnconfigure((0, 1, 2), weight=1, uniform="equal")
        
        # Pool Card 1: System Net Profit Margin
        self.card_raw = ctk.CTkFrame(pool_frame, fg_color="#313244", corner_radius=10, border_width=1, border_color="#cba6f7")
        self.card_raw.grid(row=0, column=0, padx=6, pady=5, sticky="nsew")
        ctk.CTkLabel(self.card_raw, text="TOTAL NET SYSTEM PROFIT", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a6adc8").pack(pady=(12,0))
        self.lbl_raw_num = ctk.CTkLabel(self.card_raw, textvariable=self.raw_profit_var, font=ctk.CTkFont(family="Consolas", size=20, weight="bold"), text_color="#cba6f7")
        self.lbl_raw_num.pack(pady=12)
        
        # Pool Card 2: Divine Charity Deductions (5% FiSabilillah)
        card_charity = ctk.CTkFrame(pool_frame, fg_color="#181825", corner_radius=10, border_width=2, border_color="#f9e2af")
        card_charity.grid(row=0, column=1, padx=6, pady=5, sticky="nsew")
        ctk.CTkLabel(card_charity, text="ALLAH KA RASTA (CHARITY - 5%)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#f9e2af").pack(pady=(12,0))
        lbl_charity_num = ctk.CTkLabel(card_charity, textvariable=self.charity_var, font=ctk.CTkFont(family="Consolas", size=20, weight="bold"), text_color="#f9e2af")
        lbl_charity_num.pack(pady=12)
        
        # Pool Card 3: Net Distributable Pool Amount (95%)
        card_dist = ctk.CTkFrame(pool_frame, fg_color="#313244", corner_radius=10, border_width=1, border_color="#89b4fa")
        card_dist.grid(row=0, column=2, padx=6, pady=5, sticky="nsew")
        ctk.CTkLabel(card_dist, text="NET DISTRIBUTABLE POOL (95%)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a6adc8").pack(pady=(12,0))
        lbl_dist_num = ctk.CTkLabel(card_dist, textvariable=self.distributable_var, font=ctk.CTkFont(family="Consolas", size=20, weight="bold"), text_color="#89b4fa")
        lbl_dist_num.pack(pady=12)

        # --- Lower Strategic Block: Left Side Owner Cards, Right Side Ledger Logs ---
        split_body_frame = ctk.CTkFrame(self, fg_color="transparent")
        split_body_frame.pack(fill="both", expand=True, padx=15, pady=5)
        split_body_frame.columnconfigure(0, weight=4, uniform="body_split")
        split_body_frame.columnconfigure(1, weight=5, uniform="body_split")
        
        # Left Workspace container for dynamic Owners ledgers stacks cards
        owners_stack = ctk.CTkFrame(split_body_frame, fg_color="transparent")
        owners_stack.grid(row=0, column=0, padx=(0,6), pady=0, sticky="nsew")
        
        # Owner Section Card A: Muhammad Afzal (20%)
        card_afzal = ctk.CTkFrame(owners_stack, fg_color="#313244", corner_radius=8, border_width=1, border_color="#45475a")
        card_afzal.pack(fill="x", pady=(0,8))
        ctk.CTkLabel(card_afzal, text="MUHAMMAD AFZAL SHARE (20%)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#fab387").pack(anchor="w", padx=15, pady=(8,2))
        lbl_afzal_val = ctk.CTkLabel(card_afzal, textvariable=self.share_afzal_var, font=ctk.CTkFont(family="Consolas", size=18, weight="bold"), text_color="#fab387")
        lbl_afzal_val.pack(anchor="w", padx=15, pady=(0,8))
        
        # Owner Section Card B: Haji Muhammad Nadir (30%)
        card_nadir = ctk.CTkFrame(owners_stack, fg_color="#313244", corner_radius=8, border_width=1, border_color="#45475a")
        card_nadir.pack(fill="x", pady=8)
        ctk.CTkLabel(card_nadir, text="HAJI MUHAMMAD NADIR SHARE (30%)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#a6e3a1").pack(anchor="w", padx=15, pady=(8,2))
        lbl_nadir_val = ctk.CTkLabel(card_nadir, textvariable=self.share_nadir_var, font=ctk.CTkFont(family="Consolas", size=18, weight="bold"), text_color="#a6e3a1")
        lbl_nadir_val.pack(anchor="w", padx=15, pady=(0,8))
        
        # Owner Section Card C: Haji Muhammad Hayat (50%)
        card_hayat = ctk.CTkFrame(owners_stack, fg_color="#313244", corner_radius=8, border_width=1, border_color="#45475a")
        card_hayat.pack(fill="x", pady=8)
        ctk.CTkLabel(card_hayat, text="HAJI MUHAMMAD HAYAT SHARE (50%)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94e2d5").pack(anchor="w", padx=15, pady=(8,2))
        lbl_hayat_val = ctk.CTkLabel(card_hayat, textvariable=self.share_hayat_var, font=ctk.CTkFont(family="Consolas", size=18, weight="bold"), text_color="#94e2d5")
        lbl_hayat_val.pack(anchor="w", padx=15, pady=(0,8))
        
        # Right Side Visual Statement Text Terminal Console Wrapper
        console_frame = ctk.CTkFrame(split_body_frame, fg_color="#181825", corner_radius=10)
        console_frame.grid(row=0, column=1, padx=(6,0), pady=0, sticky="nsew")
        
        lbl_log_title = ctk.CTkLabel(console_frame, text="Audit Trail Allocation Document Log Viewer", 
                                     font=ctk.CTkFont(weight="bold"), text_color="#a6adc8")
        lbl_log_title.pack(anchor="w", padx=15, pady=8)
        
        self.txt_audit_log = ctk.CTkTextbox(console_frame, fg_color="#1e1e2e", font=ctk.CTkFont(family="Consolas", size=12), text_color="#cdd6f4")
        self.txt_audit_log.pack(fill="both", expand=True, padx=15, pady=(0,15))
        self.txt_audit_log.configure(state="disabled")

    def calculate_equity_distribution(self):
        """Pulls raw matrix numbers from background tables and maps out equity arrays."""
        start_date_str = self.dt_start.get_date().strftime('%Y-%m-%d')
        end_date_str = self.dt_end.get_date().strftime('%Y-%m-%d')
        
        conn = connect_database()
        if not conn:
            messagebox.showerror("Network Fault", "Unable to pull live ledger nodes from master database node.")
            return
            
        try:
            cur = conn.cursor()
            
            # Step A: Aggregate Total Gross Revenue Streams from Safe Confirmed Bookings
            rev_sql = """
                SELECT COALESCE(SUM(number_of_guests * per_person_charge), 0) 
                FROM bookings 
                WHERE booking_date BETWEEN %s AND %s AND booking_status != 'Cancelled'
            """
            cur.execute(rev_sql, (start_date_str, end_date_str))
            gross_revenue = float(cur.fetchone()[0])
            
            # Step B: Aggregate Combined Expenses Stream Pools Consolidated Metrics
            exp_sql = """
                SELECT COALESCE(SUM(amount), 0) 
                FROM expenses 
                WHERE expense_date BETWEEN %s AND %s
            """
            cur.execute(exp_sql, (start_date_str, end_date_str))
            total_expenses = float(cur.fetchone()[0])
            
            conn.close()
            
            # Step C: Real Dynamic Audit Computation Architecture Delta Block
            net_system_profit = gross_revenue - total_expenses
            
            # Reset and evaluate logic vectors based on positive surplus vs operational deficit states
            if net_system_profit > 0:
                # Standard Blessed Operation Sequence Path Logic
                charity_allocation = net_system_profit * 0.05
                net_distributable_pool = net_system_profit - charity_allocation
                
                afzal_equity_cut = net_distributable_pool * 0.20
                nadir_equity_cut = net_distributable_pool * 0.30
                hayat_equity_cut = net_distributable_pool * 0.50
                
                self.card_raw.configure(border_color="#cba6f7")
                self.lbl_raw_num.configure(text_color="#cba6f7")
            else:
                # System Deficit / Zero Profit Exception Handling Protocol
                charity_allocation = 0.0
                net_distributable_pool = net_system_profit # Reflect total net loss sequence
                
                afzal_equity_cut = 0.0
                nadir_equity_cut = 0.0
                hayat_equity_cut = 0.0
                
                self.card_raw.configure(border_color="#f38ba8")
                self.lbl_raw_num.configure(text_color="#f38ba8")
                
            # Direct Injections to UI Interface Strings Arrays
            self.raw_profit_var.set(f"PKR {net_system_profit:,.2f}")
            self.charity_var.set(f"PKR {charity_allocation:,.2f}")
            self.distributable_var.set(f"PKR {net_distributable_pool:,.2f}")
            
            self.share_afzal_var.set(f"PKR {afzal_equity_cut:,.2f}")
            self.share_nadir_var.set(f"PKR {nadir_equity_cut:,.2f}")
            self.share_hayat_var.set(f"PKR {hayat_equity_cut:,.2f}")
            
            # Print the formatted text matrix into console screen wrapper
            self.render_text_audit_logs(start_date_str, end_date_str, gross_revenue, total_expenses, 
                                        net_system_profit, charity_allocation, net_distributable_pool,
                                        afzal_equity_cut, nadir_equity_cut, hayat_equity_cut)
            
        except Exception as dynamic_fault:
            if conn: conn.close()
            messagebox.showerror("Execution Fault", f"Could not map allocation summaries logs matrix:\n{str(dynamic_fault)}")

    def render_text_audit_logs(self, s_d, e_d, rev, exp, profit, charity, pool, a_cut, n_cut, h_cut):
        """Prints a gorgeous terminal legal audit trail to reassure system operators."""
        self.txt_audit_log.configure(state="normal")
        self.txt_audit_log.delete("1.0", "end")
        
        bar = "=" * 62 + "\n"
        dot = "-" * 62 + "\n"
        
        log = ""
        log += bar
        log += f" MARQUEE MANAGEMENT CORE PARTNERSHIP AUDIT LEDGER TRAIL\n"
        log += f" TARGET RANGE MARGIN: {s_d} TO {e_d}\n"
        log += bar
        log += f" [>] Total Generated Gross Revenue : PKR {rev:,.2f}\n"
        log += f" [<] Total Internal System Outflow : PKR {exp:,.2f}\n"
        log += dot
        
        if profit >= 0:
            log += f" [+] CONSOLIDATED SYSTEM NET PROFIT: PKR {profit:,.2f}\n"
            log += bar
            log += f"  * Divine Charity Deduct (5.0%)  : PKR {charity:,.2f}\n"
            log += f"  = Net Pool For Distribution     : PKR {pool:,.2f}\n"
            log += bar
            log += " OWNERS INTERNAL DISBURSEMENT MAP EXTRACTIONS:\n"
            log += dot
            log += f"  [Share 20%] Muhammad Afzal      : PKR {a_cut:,.2f}\n"
            log += f"  [Share 30%] Haji Muhammad Nadir : PKR {n_cut:,.2f}\n"
            log += f"  [Share 50%] Haji Muhammad Hayat : PKR {h_cut:,.2f}\n"
        else:
            log += f" [-] UNFORTUNATE CRITICAL BUSINESS LOSS DETECTED: PKR {abs(profit):,.2f}\n"
            log += bar
            log += "  ! Operational alert notice: Distribution pools skipped.\n"
            log += "  ! Partnership equity balances remain locked until surplus.\n"
            
        log += bar
        self.txt_audit_log.insert("1.0", log)
        self.txt_audit_log.configure(state="disabled")

    def export_distribution_matrix(self):
        """Serializes current active split matrix logs layout to permanent disk sheets files."""
        if not PANDAS_AVAILABLE:
            messagebox.showerror("Dependency Issue", "Pandas environment module is missing from the underlying host computer runtime.")
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Matrix Document Worksheet", "*.xlsx"), ("Flat CSV Stream", "*.csv")]
        )
        if not save_path: return
        
        try:
            # Build structured dictionary dataset to frame cleanly
            statement_data = {
                "Financial Metric / Entity Component": [
                    "Statement Start Date", "Statement End Date", "Gross Revenue Pipeline Inflow",
                    "Consolidated Expenses Outflow", "Net Overall Business Profit/Loss Delta",
                    "Allah Ka Rasta Charity Wallet Split (5%)", "Net Capital Distribution Pool Remaining (95%)",
                    "Muhammad Afzal Payout Share Metric (20%)", "Haji Muhammad Nadir Payout Share Metric (30%)",
                    "Haji Muhammad Hayat Payout Share Metric (50%)"
                ],
                "Calculated Audited Values Status (PKR / Meta)": [
                    self.dt_start.get_date().strftime('%Y-%m-%d'), self.dt_end.get_date().strftime('%Y-%m-%d'),
                    self.raw_profit_var.get(), "Calculated via core database", self.raw_profit_var.get(),
                    self.charity_var.get(), self.distributable_var.get(),
                    self.share_afzal_var.get(), self.share_nadir_var.get(), self.share_hayat_var.get()
                ]
            }
            
            df = pd.DataFrame(statement_data)
            if save_path.endswith(".xlsx"):
                df.to_excel(save_path, index=False)
            else:
                df.to_csv(save_path, index=False)
                
            messagebox.showinfo("Export Perfect", f"Equity Shareholder Sheet logged successfully at:\n{save_path}")
        except Exception as save_fault:
            messagebox.showerror("Export Interrupted", f"Failed to serialize partition tables matrices files:\n{save_fault}")