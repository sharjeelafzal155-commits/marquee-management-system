# -*- coding: utf-8 -*-
# Save as: forms/khaata_milk_dairy_form.py

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

class KhaataMilkDairyForm(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        # Premium Dark Palette Configuration Integration
        super().__init__(master, fg_color="#1e1e2e", **kwargs)
        self.master = master
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.selected_id = None
        
        # Enforce exact Schema Structures before rendering layouts
        self.ensure_database_schema_layers()
        
        # Initialize UI reactive input tracking variables
        self.initialize_form_variables()
        
        # Build UI Screen Elements Matrix Grid
        self.setup_ui_components()
        
        # Fetch operational components data datasets
        self.refresh_booking_dropdown_list()
        self.refresh_table_dataset()

    def ensure_database_schema_layers(self):
        """Creates or alters tables to enforce strict double-entry system rules architecture."""
        conn = connect_database()
        if not conn:
            return
        try:
            cur = conn.cursor()
            
            # 1. Main expenses master infrastructure lookup table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    expense_type VARCHAR(100) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    expense_date DATE NOT NULL,
                    paid_by VARCHAR(100) NOT NULL,
                    payment_method VARCHAR(50) NOT NULL,
                    reference_no VARCHAR(100) DEFAULT NULL,
                    attachment_path VARCHAR(255) DEFAULT NULL,
                    status VARCHAR(50) DEFAULT 'Paid'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # 2. Sub-Khaata specialized metrics ledger schema execution map for Milk & Dairy
            cur.execute("""
                CREATE TABLE IF NOT EXISTS khaata_milk_dairy (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    category VARCHAR(100) DEFAULT 'Milk & Dairy',
                    item_name VARCHAR(100) NOT NULL,
                    quantity DECIMAL(10,2) NOT NULL,
                    unit VARCHAR(20) DEFAULT 'litre',
                    price_per_unit DECIMAL(10,2) NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    advance_paid DECIMAL(10,2) DEFAULT 0.00,
                    remaining_balance DECIMAL(10,2) DEFAULT 0.00,
                    supplier_name VARCHAR(100) NOT NULL,
                    purchase_date DATE NOT NULL,
                    booking_id INT DEFAULT NULL,
                    linked_expense_id INT DEFAULT NULL,
                    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL,
                    FOREIGN KEY (linked_expense_id) REFERENCES expenses(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            conn.commit()
            conn.close()
        except Exception as schema_fault:
            messagebox.showerror("Database Enforcer Crash", f"Could not sync table specifications:\n{str(schema_fault)}")

    def initialize_form_variables(self):
        """Instantiates variable handles with live cross-calculation math listeners."""
        self.v_item = tk.StringVar()
        self.v_qty = tk.StringVar(value="0")
        self.v_price = tk.StringVar(value="0")
        self.v_advance = tk.StringVar(value="0")
        self.v_supplier = tk.StringVar()
        
        # Structural booking selections mappings
        self.v_booking_selection = tk.StringVar(value="None / General Stock")
        self.booking_id_map = {} # Context dictionary mapper stores text-to-ID keys
        
        # Real-time reactive calculation layout label strings
        self.lbl_calc_total = tk.StringVar(value="PKR 0.00")
        self.lbl_calc_bal = tk.StringVar(value="PKR 0.00")
        
        # Inject automated calculation change listeners pipelines
        self.v_qty.trace_add("write", self.execute_live_ledger_math)
        self.v_price.trace_add("write", self.execute_live_ledger_math)
        self.v_advance.trace_add("write", self.execute_live_ledger_math)

    def execute_live_ledger_math(self, *args):
        """Processes dynamic live calculations values variables loops instantly."""
        try:
            qty = float(self.v_qty.get()) if self.v_qty.get().replace('.', '', 1).isdigit() else 0.0
            rate = float(self.v_price.get()) if self.v_price.get().replace('.', '', 1).isdigit() else 0.0
            advance = float(self.v_advance.get()) if self.v_advance.get().replace('.', '', 1).isdigit() else 0.0
            
            total = qty * rate
            balance = total - advance
            
            self.lbl_calc_total.set(f"PKR {total:,.2f}")
            self.lbl_calc_bal.set(f"PKR {balance:,.2f}")
        except Exception:
            self.lbl_calc_total.set("PKR 0.00")
            self.lbl_calc_bal.set("PKR 0.00")

    def setup_ui_components(self):
        """Draws consistent premium dark components interfaces maps splits frames grids."""
        self.grid_columnconfigure(0, weight=2) # Left Editor Panel Block
        self.grid_columnconfigure(1, weight=3) # Right Live Stream Database Ledger Block
        self.grid_rowconfigure(0, weight=1)
        
        # --------------------------------------------------------------------------
        # LEFT EDITOR STUDIO CARD FRAME
        # --------------------------------------------------------------------------
        editor_frame = ctk.CTkFrame(self, fg_color="#313244", corner_radius=12)
        editor_frame.grid(row=0, column=0, padx=(0, 15), sticky="nsew")
        
        lbl_screen_header = ctk.CTkLabel(
            editor_frame, text="Milk & Dairy Ledger",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#cba6f7"
        )
        lbl_screen_header.pack(anchor="w", padx=20, pady=(20, 10))
        
        scroll_container = ctk.CTkScrollableFrame(editor_frame, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Input: Item Name Definition
        ctk.CTkLabel(scroll_container, text="Item Description (e.g. Milk, Khoya, Cream, Dahi):", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5, pady=(4, 0))
        ctk.CTkEntry(scroll_container, textvariable=self.v_item, fg_color="#1e1e2e", text_color="#cdd6f4", border_color="#45475a", height=32).pack(fill="x", padx=5, pady=2)
        
        # Input: Supplier Reference 
        ctk.CTkLabel(scroll_container, text="Supplier / Dairy Farm Name:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5, pady=(6, 0))
        ctk.CTkEntry(scroll_container, textvariable=self.v_supplier, fg_color="#1e1e2e", text_color="#cdd6f4", border_color="#45475a", height=32).pack(fill="x", padx=5, pady=2)
        
        # Inputs Dual Matrix: Quantities and Rates per metrics unit
        metrics_row = ctk.CTkFrame(scroll_container, fg_color="transparent")
        metrics_row.pack(fill="x", pady=4)
        metrics_row.grid_columnconfigure((0, 1), weight=1)
        
        qty_block = ctk.CTkFrame(metrics_row, fg_color="transparent")
        qty_block.grid(row=0, column=0, padx=(0, 4), sticky="nsew")
        ctk.CTkLabel(qty_block, text="Quantity (Ltr/KG):", text_color="#cdd6f4", font=("Segoe UI", 11)).pack(anchor="w", padx=5)
        ctk.CTkEntry(qty_block, textvariable=self.v_qty, fg_color="#1e1e2e", border_color="#45475a").pack(fill="x", pady=2)
        
        rate_block = ctk.CTkFrame(metrics_row, fg_color="transparent")
        rate_block.grid(row=0, column=1, padx=(4, 0), sticky="nsew")
        ctk.CTkLabel(rate_block, text="Price Per Unit:", text_color="#cdd6f4", font=("Segoe UI", 11)).pack(anchor="w", padx=5)
        ctk.CTkEntry(rate_block, textvariable=self.v_price, fg_color="#1e1e2e", border_color="#45475a").pack(fill="x", pady=2)

        # Input: Operational Cash Advance Paid Amount
        ctk.CTkLabel(scroll_container, text="Cash Amount Paid to Supplier (Advance):", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5, pady=(6, 0))
        ctk.CTkEntry(scroll_container, textvariable=self.v_advance, fg_color="#1e1e2e", text_color="#cdd6f4", border_color="#45475a", height=32).pack(fill="x", padx=5, pady=2)

        # Input Row: Target Booking Mappings Selector Dropdowns Matrix
        ctk.CTkLabel(scroll_container, text="Link Transaction to Active Event Booking Slot:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5, pady=(6, 0))
        self.dropdown_bookings = ctk.CTkOptionMenu(
            scroll_container, variable=self.v_booking_selection,
            values="None / General Stock", fg_color="#1e1e2e", button_color="#45475a", dropdown_fg_color="#1e1e2e", text_color="#cdd6f4"
        )
        self.dropdown_bookings.pack(fill="x", padx=5, pady=2)

        # Input: Calendar Purchase Operational Execution Timeline Date
        ctk.CTkLabel(scroll_container, text="Purchase Timeline Execution Date:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5, pady=(6, 0))
        self.dt_purchase = DateEntry(scroll_container, width=16, background='#313244', foreground='#cdd6f4', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.dt_purchase.pack(fill="x", padx=5, pady=4)

        # --------------------------------------------------------------------------
        # SYSTEM FINANCIAL INTELLIGENCE REAL-TIME HUD INDICATORS
        # --------------------------------------------------------------------------
        calculated_hud_panel = ctk.CTkFrame(scroll_container, fg_color="#1e1e2e", corner_radius=8, border_width=1, border_color="#45475a")
        calculated_hud_panel.pack(fill="x", pady=15, padx=5)
        calculated_hud_panel.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(calculated_hud_panel, text="Total Invoiced Outlay:", text_color="#a6adc8", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")
        ctk.CTkLabel(calculated_hud_panel, textvariable=self.lbl_calc_total, text_color="#a6e3a1", font=("Segoe UI", 14, "bold")).grid(row=1, column=0, padx=12, pady=(0, 8), sticky="w")
        
        ctk.CTkLabel(calculated_hud_panel, text="Khaata Outstanding Unpaid Balance:", text_color="#a6adc8", font=("Segoe UI", 11, "bold")).grid(row=0, column=1, padx=12, pady=(8, 2), sticky="e")
        ctk.CTkLabel(calculated_hud_panel, textvariable=self.lbl_calc_bal, text_color="#f38ba8", font=("Segoe UI", 14, "bold")).grid(row=1, column=1, padx=12, pady=(0, 8), sticky="e")

        # Command Operations Canvas Controls Buttons Row Layout Strip
        btn_layout_strip = ctk.CTkFrame(editor_frame, fg_color="transparent")
        btn_layout_strip.pack(fill="x", side="bottom", padx=15, pady=15)
        btn_layout_strip.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkButton(btn_layout_strip, text="Save Entry", font=("Segoe UI", 12, "bold"), fg_color="#a6e3a1", text_color="#11111b", hover_color="#89b4fa", height=36, command=self.execute_save_transaction_pipeline).grid(row=0, column=0, padx=2, sticky="nsew")
        ctk.CTkButton(btn_layout_strip, text="Update Entry", font=("Segoe UI", 12, "bold"), fg_color="#f9e2af", text_color="#11111b", hover_color="#89b4fa", height=36, command=self.execute_update_transaction_pipeline).grid(row=0, column=1, padx=2, sticky="nsew")
        ctk.CTkButton(btn_layout_strip, text="Delete Entry", font=("Segoe UI", 12, "bold"), fg_color="#f38ba8", text_color="#11111b", hover_color="#89b4fa", height=36, command=self.execute_purge_transaction_pipeline).grid(row=0, column=2, padx=2, sticky="nsew")

        # --------------------------------------------------------------------------
        # RIGHT MONITOR STREAM: HISTORICAL ENTRIES LEDGER VIEWPORT
        # --------------------------------------------------------------------------
        monitor_frame = ctk.CTkFrame(self, fg_color="#313244", corner_radius=12)
        monitor_frame.grid(row=0, column=1, sticky="nsew")
        
        header_actions_row = ctk.CTkFrame(monitor_frame, fg_color="transparent")
        header_actions_row.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_actions_row, text="Dairy Transaction History",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#cba6f7"
        ).pack(side="left")
        
        ctk.CTkButton(
            header_actions_row, text="Export Sheet", font=("Segoe UI", 11, "bold"),
            fg_color="#89b4fa", text_color="#11111b", width=90, height=28,
            command=self.execute_excel_export_matrix
        ).pack(side="right")
        
        # Responsive Dynamic List Content Wrapper Viewport Canvas Layout
        list_scroller_viewport = ctk.CTkScrollableFrame(monitor_frame, fg_color="#1e1e2e", corner_radius=10, border_width=1, border_color="#45475a")
        list_scroller_viewport.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.render_canvas_records_wrapper = list_scroller_viewport

    def refresh_booking_dropdown_list(self):
        """Pulls dynamic data mapping sets of identities from booking registries columns."""
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, customer_name, event_date FROM bookings WHERE booking_status  != 'Cancelled' ORDER BY event_date ASC")
            dataset = cur.fetchall()
            conn.close()
            
            options_pool = ["None / General Stock"]
            self.booking_id_map = {}
            
            for b_id, name, ev_date in dataset:
                mapping_string = f"ID: {b_id} | {name} ({ev_date})"
                options_pool.append(mapping_string)
                self.booking_id_map[mapping_string] = b_id
                
            self.dropdown_bookings.configure(values=options_pool)
        except Exception as query_fault:
            print(f"[Dropdown Sync Warning] Error mapping dropdown connection sets: {query_fault}")

    def refresh_table_dataset(self):
        """Flushes and loads current rows sets blocks from MariaDB schemas inside views elements."""
        for active_widget in self.render_canvas_records_wrapper.winfo_children():
            active_widget.destroy()
            
        # Draw explicit table grid header bars elements
        headers_strip = ctk.CTkFrame(self.render_canvas_records_wrapper, fg_color="#181825", corner_radius=6, height=28)
        headers_strip.pack(fill="x", padx=5, pady=4)
        
        col_mappings = [("Item Details", 0.35), ("Purchase Date", 0.20), ("Total Outlay", 0.25), ("Balance Due", 0.20)]
        for col_name, scale_factor in col_mappings:
            lbl = ctk.CTkLabel(headers_strip, text=col_name, text_color="#a6adc8", font=("Segoe UI", 11, "bold"), anchor="w")
            lbl.pack(side="left", fill="x", expand=True, padx=8)

        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, item_name, quantity, price_per_unit, total_amount, 
                       advance_paid, remaining_balance, supplier_name, purchase_date, 
                       booking_id, linked_expense_id 
                FROM khaata_milk_dairy 
                ORDER BY purchase_date DESC
            """)
            rows = cur.fetchall()
            conn.close()
            
            for row in rows:
                db_id, item, qty, price, total, advance, balance, supplier, p_date, b_id, exp_id = row
                
                row_item_button = ctk.CTkFrame(
                    self.render_canvas_records_wrapper, fg_color="#313244",
                    corner_radius=6, height=42
                )
                row_item_button.pack(fill="x", padx=5, pady=2)
                row_item_button.bind("<Button-1>", lambda event, target_id=db_id: self.load_selected_row_to_form(target_id))
                
                # Render content metrics parameters structures lines segments
                lbl_desc = ctk.CTkLabel(row_item_button, text=f"{item} ({qty} kg)", text_color="#cdd6f4", font=("Segoe UI", 11, "bold"), anchor="w")
                lbl_desc.pack(side="left", padx=10, fill="x", expand=True)
                lbl_desc.bind("<Button-1>", lambda event, target_id=db_id: self.load_selected_row_to_form(target_id))

                lbl_time = ctk.CTkLabel(row_item_button, text=f"{p_date}", text_color="#a6adc8", font=("Segoe UI", 11), anchor="w")
                lbl_time.pack(side="left", padx=10, fill="x", expand=True)
                lbl_time.bind("<Button-1>", lambda event, target_id=db_id: self.load_selected_row_to_form(target_id))

                lbl_tot = ctk.CTkLabel(row_item_button, text=f"PKR {total:,.0f}", text_color="#a6e3a1", font=("Segoe UI", 11, "bold"), anchor="w")
                lbl_tot.pack(side="left", padx=10, fill="x", expand=True)
                lbl_tot.bind("<Button-1>", lambda event, target_id=db_id: self.load_selected_row_to_form(target_id))

                balance_marker_color = "#f38ba8" if balance > 0 else "#a6e3a1"
                lbl_bal = ctk.CTkLabel(row_item_button, text=f"PKR {balance:,.0f}", text_color=balance_marker_color, font=("Segoe UI", 11, "bold"), anchor="w")
                lbl_bal.pack(side="left", padx=10, fill="x", expand=True)
                lbl_bal.bind("<Button-1>", lambda event, target_id=db_id: self.load_selected_row_to_form(target_id))
                
        except Exception as load_fault:
            messagebox.showerror("SQL Read Fault", f"Could not populate ledger history panel stream:\n{str(load_fault)}")

    def load_selected_row_to_form(self, record_id):
        """Binds targeted data attributes backward into interactive inputs variables fields elements."""
        self.selected_id = record_id
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT item_name, quantity, price_per_unit, advance_paid, supplier_name, purchase_date, booking_id 
                FROM khaata_milk_dairy WHERE id = %s
            """, (record_id,))
            res = cur.fetchone()
            conn.close()
            
            if res:
                item, qty, price, advance, supplier, p_date, b_id = res
                self.v_item.set(item)
                self.v_qty.set(str(qty))
                self.v_price.set(str(price))
                self.v_advance.set(str(advance))
                self.v_supplier.set(supplier)
                self.dt_purchase.set_date(p_date)
                
                # Rollback dropdown components selectors to matched index targets keys
                matched_dropdown_string = "None / General Stock"
                if b_id:
                    for text_str, internal_id in self.booking_id_map.items():
                        if internal_id == b_id:
                            matched_dropdown_string = text_str
                            break
                self.v_booking_selection.set(matched_dropdown_string)
                
                # Recalculate displays metrics output labels parameters strings
                self.execute_live_ledger_math()
        except Exception as fetch_fault:
            messagebox.showerror("Form Assignment Crash", str(fetch_fault))

    def execute_save_transaction_pipeline(self):
        """Handles double entry pipeline inserting into both dairy sub-khaata and shared expenses rows."""
        if not self.v_item.get().strip() or not self.v_supplier.get().strip():
            messagebox.showwarning("Validation Error", "Item details and Supplier credentials cannot be blank.")
            return
            
        conn = connect_database()
        if not conn: return
        try:
            qty = float(self.v_qty.get()) if self.v_qty.get().replace('.', '', 1).isdigit() else 0.0
            rate = float(self.v_price.get()) if self.v_price.get().replace('.', '', 1).isdigit() else 0.0
            advance = float(self.v_advance.get()) if self.v_advance.get().replace('.', '', 1).isdigit() else 0.0
            total_outlay = qty * rate
            remaining_due = total_outlay - advance
            
            chosen_booking_str = self.v_booking_selection.get()
            target_booking_id = self.booking_id_map.get(chosen_booking_str, None)
            
            cur = conn.cursor()
            
            # --------------------------------------------------------------------------
            # DOUBLE ENTRY SYSTEM: INSERT PIPELINE INTO INTEGRATED SHARED EXPENSES TABLE
            # --------------------------------------------------------------------------
            expense_status = "Paid"
            if remaining_due > 0 and advance > 0: expense_status = "Partial"
            elif remaining_due > 0 and advance == 0: expense_status = "Pending"
            
            expense_narrative_reference = f"Supplier: {self.v_supplier.get().strip()} | Item: {self.v_item.get().strip()}"
            
            cur.execute("""
                INSERT INTO expenses (
                    expense_type, amount, expense_date, paid_by, payment_method, reference_no, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                "Dairy & Milk Khaata",
                advance,  # actual liquid cash paid out from cash counter
                self.dt_purchase.get_date(),
                "Marquee Counter Cash",
                "Cash",
                expense_narrative_reference,
                expense_status
            ))
            
            generated_expense_master_id = cur.lastrowid
            
            # --------------------------------------------------------------------------
            # SAVE PRIMARY ENTRIES BLOCK INTO SPECIFIC DAIRY SUB-KHAATA TABLE
            # --------------------------------------------------------------------------
            cur.execute("""
                INSERT INTO khaata_milk_dairy (
                    item_name, quantity, price_per_unit, total_amount, advance_paid, 
                    remaining_balance, supplier_name, purchase_date, booking_id, linked_expense_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.v_item.get().strip(),
                qty,
                rate,
                total_outlay,
                advance,
                remaining_due,
                self.v_supplier.get().strip(),
                self.dt_purchase.get_date(),
                target_booking_id,
                generated_expense_master_id
            ))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Double Entry Log Success", "Transaction updated into Dairy Sub-Khaata and synced onto Master Expense stream.")
            self.clear_form_input_fields()
            self.refresh_table_dataset()
            
            # Trigger real time dashboard UI sync components updates
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
                
        except Exception as tx_crash:
            messagebox.showerror("SQL Execution Failure", f"Transaction engine rolled back mutations chains:\n{str(tx_crash)}")

    def execute_update_transaction_pipeline(self):
        """Mutates existing dataset row maps safely across both linked table coordinates matrices."""
        if not self.selected_id:
            messagebox.showwarning("Context Selection Error", "Please pick a historical log block row from the tracker matrix first.")
            return
            
        conn = connect_database()
        if not conn: return
        try:
            qty = float(self.v_qty.get()) if self.v_qty.get().replace('.', '', 1).isdigit() else 0.0
            rate = float(self.v_price.get()) if self.v_price.get().replace('.', '', 1).isdigit() else 0.0
            advance = float(self.v_advance.get()) if self.v_advance.get().replace('.', '', 1).isdigit() else 0.0
            total_outlay = qty * rate
            remaining_due = total_outlay - advance
            
            chosen_booking_str = self.v_booking_selection.get()
            target_booking_id = self.booking_id_map.get(chosen_booking_str, None)
            
            cur = conn.cursor()
            
            # Retrieve currently mapped link identities keys values strings
            cur.execute("SELECT linked_expense_id FROM khaata_milk_dairy WHERE id = %s", (self.selected_id,))
            exp_link_res = cur.fetchone()
            
            expense_status = "Paid"
            if remaining_due > 0 and advance > 0: expense_status = "Partial"
            elif remaining_due > 0 and advance == 0: expense_status = "Pending"
            
            expense_narrative_reference = f"Supplier: {self.v_supplier.get().strip()} | Item: {self.v_item.get().strip()}"
            
            if exp_link_res and exp_link_res[0]:
                # Mutate shared expenses cluster rows configurations
                cur.execute("""
                    UPDATE expenses SET 
                        amount = %s, expense_date = %s, reference_no = %s, status = %s 
                    WHERE id = %s
                """, (advance, self.dt_purchase.get_date(), expense_narrative_reference, expense_status, exp_link_res[0]))
                
            # Mutate sub-khaata local matrix schema parameters for Dairy
            cur.execute("""
                UPDATE khaata_milk_dairy SET 
                    item_name = %s, quantity = %s, price_per_unit = %s, total_amount = %s, 
                    advance_paid = %s, remaining_balance = %s, supplier_name = %s, 
                    purchase_date = %s, booking_id = %s
                WHERE id = %s
            """, (
                self.v_item.get().strip(), qty, rate, total_outlay, advance, remaining_due,
                self.v_supplier.get().strip(), self.dt_purchase.get_date(), target_booking_id, self.selected_id
            ))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Mutations Propagated", "Modifications rewritten across cluster registers channels successfully.")
            self.clear_form_input_fields()
            self.refresh_table_dataset()
            
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
        except Exception as mutation_fault:
            messagebox.showerror("SQL Update Interrupted", str(mutation_fault))

    def execute_purge_transaction_pipeline(self):
        """Drops transaction references securely across shared tables clusters nodes completely."""
        if not self.selected_id:
            messagebox.showwarning("Target Unspecified", "Select an element row line block from history viewport canvas to remove.")
            return
            
        verify_action = messagebox.askyesno("Destructive Security Request", "Are you sure you want to delete this transaction and remove its synced record from Master Expenses?")
        if not verify_action: return
        
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            
            # Fetch target linked items keys values pointers
            cur.execute("SELECT linked_expense_id FROM khaata_milk_dairy WHERE id = %s", (self.selected_id,))
            link_record = cur.fetchone()
            
            # Delete row entry from target sub-khaata table matrix layout
            cur.execute("DELETE FROM khaata_milk_dairy WHERE id = %s", (self.selected_id,))
            
            # Delete correlated row entry references from shared expenses dataset logs table layout
            if link_record and link_record[0]:
                cur.execute("DELETE FROM expenses WHERE id = %s", (link_record[0],))
                
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Purge Process Completed", "Records dropped securely across pipeline channels registries.")
            self.clear_form_input_fields()
            self.refresh_table_dataset()
            
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
        except Exception as deployment_fault:
            messagebox.showerror("Purge Cascade Failure", str(deployment_fault))

    def clear_form_input_fields(self):
        """Resets variable handles array sliders parameters pointers cleanly."""
        self.selected_id = None
        self.v_item.set("")
        self.v_qty.set("0")
        self.v_price.set("0")
        self.v_advance.set("0")
        self.v_supplier.set("")
        self.v_booking_selection.set("None / General Stock")
        self.dt_purchase.set_date(date.today())
        self.lbl_calc_total.set("PKR 0.00")
        self.lbl_calc_bal.set("PKR 0.00")

    def execute_excel_export_matrix(self):
        """Converts database arrays structures to target desktop storage files maps matrices layers."""
        conn = connect_database()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM khaata_milk_dairy ORDER BY purchase_date DESC")
            dataset = cur.fetchall()
            headers = [col_desc[0] for col_desc in cur.description]
            conn.close()
            
            save_dest_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx", 
                filetypes=[("Excel Matrix Data Worksheet","*.xlsx"),("CSV Flat Sheet Streams","*.csv")]
            )
            if not save_dest_path: return
            
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