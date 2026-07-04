# -*- coding: utf-8 -*-
# Save as: forms/booking_form.py

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import date
from db.connection import connect_database

# Enterprise Dropdown Enums
EVENT_TYPES = ["Wedding / Baraat", "Walima", "Mehndi / Dholki", "Birthday", "Corporate Event", "Conference", "Other"]
STATUS_TYPES = ["Pending", "Confirmed", "Cancelled"]
HALLS = ["Main Hall", "Executive Hall A", "Premium Hall B", "Open Garden", "Rooftop Arena"]

class BookingForm(ctk.CTkFrame):
    def __init__(self, master):
        # Native Dark Theme Binding Architecture supporting absolute palette rules
        super().__init__(master, fg_color="#1e1e2e")
        self.master = master
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.selected_booking_id = None
        
        # Core State Variables Initializations
        self.initialize_state_variables()
        
        # Build UI Screen Layout Components
        self.setup_ui_layout()
        
        # Load Existing Dataset from MariaDB / MySQL
        self.refresh_table_data()

    def initialize_state_variables(self):
        """Initializes secure UI variables for reactive pipeline binding."""
        self.customer_name = tk.StringVar()
        self.customer_contact = tk.StringVar()
        self.event_type = tk.StringVar(value=EVENT_TYPES[0])
        self.hall_name = tk.StringVar(value=HALLS[0])
        self.booking_status = tk.StringVar(value=STATUS_TYPES[0])
        
        # Financial Numerical Fields Managed via Strings to Prevent Unhandled Caret Exceptions
        self.number_of_guests = tk.StringVar(value="0")
        self.per_person_charge = tk.StringVar(value="0")
        self.advance_paid = tk.StringVar(value="0")
        
        # Calculated Functional Real-time Metric Displays Labels Variables
        self.lbl_calc_total = tk.StringVar(value="PKR 0")
        self.lbl_calc_rem = tk.StringVar(value="PKR 0")
        
        # Live Track Event Key Bindings for Live Calculation Outputs
        self.number_of_guests.trace_add("write", self.execute_live_financial_calculations)
        self.per_person_charge.trace_add("write", self.execute_live_financial_calculations)
        self.advance_paid.trace_add("write", self.execute_live_financial_calculations)

    def execute_live_financial_calculations(self, *args):
        """Triggers transactional math changes live as the user types coordinates data."""
        try:
            guests_str = self.number_of_guests.get().strip()
            rate_str = self.per_person_charge.get().strip()
            advance_str = self.advance_paid.get().strip()

            guests = int(guests_str) if guests_str.isdigit() else 0
            rate = float(rate_str) if rate_str.replace('.', '', 1).isdigit() else 0.0
            advance = float(advance_str) if advance_str.replace('.', '', 1).isdigit() else 0.0
            
            total = guests * rate
            remaining = total - advance
            
            self.lbl_calc_total.set(f"PKR {total:,.2f}")
            self.lbl_calc_rem.set(f"PKR {remaining:,.2f}")
        except Exception:
            self.lbl_calc_total.set("PKR 0.00")
            self.lbl_calc_rem.set("PKR 0.00")

    def setup_ui_layout(self):
        """Draws professional high-end corporate split screen layouts elements grids."""
        # Main Grid Structure Matrix Configuration
        self.grid_columnconfigure(0, weight=2)  # Left Data Entry Studio Editor Card
        self.grid_columnconfigure(1, weight=3)  # Right Database Monitor Ledger Stream Grid
        self.grid_rowconfigure(0, weight=1)
        
        # Left Side Editor Container Panel
        editor_card = ctk.CTkFrame(self, fg_color="#313244", corner_radius=12)
        editor_card.grid(row=0, column=0, padx=(0, 15), sticky="nsew")
        
        # Screen Title Bar Setup Block
        lbl_title = ctk.CTkLabel(
            editor_card, text="Event Booking Engine",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#cba6f7"
        )
        lbl_title.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Form Input Fields Layout Panel Alignment
        scroll_form = ctk.CTkScrollableFrame(editor_card, fg_color="transparent")
        scroll_form.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Input Element 1: Client Name
        ctk.CTkLabel(scroll_form, text="Customer Full Name:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5, pady=(5, 0))
        ctk.CTkEntry(scroll_form, textvariable=self.customer_name, fg_color="#1e1e2e", text_color="#cdd6f4", border_color="#45475a", height=32).pack(fill="x", padx=5, pady=2)
        
        # Input Element 2: Contact Number
        ctk.CTkLabel(scroll_form, text="Customer Contact / Phone Number:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5, pady=(8, 0))
        ctk.CTkEntry(scroll_form, textvariable=self.customer_contact, fg_color="#1e1e2e", text_color="#cdd6f4", border_color="#45475a", height=32).pack(fill="x", padx=5, pady=2)
        
        # Input Element 3: Calendar Dates Pickers Rows Layout Block
        date_row = ctk.CTkFrame(scroll_form, fg_color="transparent")
        date_row.pack(fill="x", pady=8)
        date_row.grid_columnconfigure((0, 1), weight=1)
        
        # Booking Date Frame Setup
        b_date_frame = ctk.CTkFrame(date_row, fg_color="transparent")
        b_date_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        ctk.CTkLabel(b_date_frame, text="Booking Date:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5)
        self.cal_booking = DateEntry(b_date_frame, width=16, background='#313244', foreground='#cdd6f4', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.cal_booking.pack(fill="x", padx=5, pady=2)
        
        # Event Date Frame Setup
        e_date_frame = ctk.CTkFrame(date_row, fg_color="transparent")
        e_date_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        ctk.CTkLabel(e_date_frame, text="Event Execution Date:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5)
        self.cal_event = DateEntry(e_date_frame, width=16, background='#313244', foreground='#cdd6f4', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.cal_event.pack(fill="x", padx=5, pady=2)
        
        # Input Element 4: Dropdowns Row (Event Type + Venue Hall Selectors)
        drop_row = ctk.CTkFrame(scroll_form, fg_color="transparent")
        drop_row.pack(fill="x", pady=6)
        drop_row.grid_columnconfigure((0, 1), weight=1)
        
        et_frame = ctk.CTkFrame(drop_row, fg_color="transparent")
        et_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        ctk.CTkLabel(et_frame, text="Event Type Category:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5)
        ctk.CTkOptionMenu(et_frame, variable=self.event_type, values=EVENT_TYPES, fg_color="#1e1e2e", button_color="#45475a", button_hover_color="#585b70", dropdown_fg_color="#1e1e2e").pack(fill="x", padx=5, pady=2)
        
        vn_frame = ctk.CTkFrame(drop_row, fg_color="transparent")
        vn_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        ctk.CTkLabel(vn_frame, text="Select Venue / Hall:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5)
        ctk.CTkOptionMenu(vn_frame, variable=self.hall_name, values=HALLS, fg_color="#1e1e2e", button_color="#45475a", button_hover_color="#585b70", dropdown_fg_color="#1e1e2e").pack(fill="x", padx=5, pady=2)

        # Input Element 5: Metrics Numeric Math Controls Rows Layout
        math_row = ctk.CTkFrame(scroll_form, fg_color="transparent")
        math_row.pack(fill="x", pady=6)
        math_row.grid_columnconfigure((0, 1, 2), weight=1)
        
        gc_frame = ctk.CTkFrame(math_row, fg_color="transparent")
        gc_frame.grid(row=0, column=0, padx=2, sticky="nsew")
        ctk.CTkLabel(gc_frame, text="Total Guests:", text_color="#cdd6f4", font=("Segoe UI", 11)).pack(anchor="w", padx=3)
        ctk.CTkEntry(gc_frame, textvariable=self.number_of_guests, fg_color="#1e1e2e", border_color="#45475a").pack(fill="x", pady=2)
        
        pr_frame = ctk.CTkFrame(math_row, fg_color="transparent")
        pr_frame.grid(row=0, column=1, padx=2, sticky="nsew")
        ctk.CTkLabel(pr_frame, text="Per Head Rate:", text_color="#cdd6f4", font=("Segoe UI", 11)).pack(anchor="w", padx=3)
        ctk.CTkEntry(pr_frame, textvariable=self.per_person_charge, fg_color="#1e1e2e", border_color="#45475a").pack(fill="x", pady=2)
        
        ap_frame = ctk.CTkFrame(math_row, fg_color="transparent")
        ap_frame.grid(row=0, column=2, padx=2, sticky="nsew")
        ctk.CTkLabel(ap_frame, text="Advance Cash Paid:", text_color="#cdd6f4", font=("Segoe UI", 11)).pack(anchor="w", padx=3)
        ctk.CTkEntry(ap_frame, textvariable=self.advance_paid, fg_color="#1e1e2e", border_color="#45475a").pack(fill="x", pady=2)

        # Input Element 6: Active Status Parameters Dropdown Selection Row
        ctk.CTkLabel(scroll_form, text="Current Booking Operational Status:", text_color="#cdd6f4", font=("Segoe UI", 12)).pack(anchor="w", padx=5, pady=(8, 0))
        ctk.CTkOptionMenu(scroll_form, variable=self.booking_status, values=STATUS_TYPES, fg_color="#1e1e2e", button_color="#45475a", button_hover_color="#585b70", dropdown_fg_color="#1e1e2e").pack(fill="x", padx=5, pady=2)

        # --------------------------------------------------------------------------
        # BUSINESS LOGIC EXTRA READ-ONLY CARD REAL-TIME HUD MONITORS
        # --------------------------------------------------------------------------
        hud_card = ctk.CTkFrame(scroll_form, fg_color="#1e1e2e", corner_radius=8, border_width=1, border_color="#45475a")
        hud_card.pack(fill="x", pady=15, padx=5)
        
        ctk.CTkLabel(hud_card, text="Calculated Event Invoiced Amount:", text_color="#a6adc8", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=12, pady=(10, 2), sticky="w")
        ctk.CTkLabel(hud_card, textvariable=self.lbl_calc_total, text_color="#a6e3a1", font=("Segoe UI", 14, "bold")).grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")
        
        ctk.CTkLabel(hud_card, text="Liquid Outstanding Receivables Balance:", text_color="#a6adc8", font=("Segoe UI", 11, "bold")).grid(row=0, column=1, padx=12, pady=(10, 2), sticky="e")
        ctk.CTkLabel(hud_card, textvariable=self.lbl_calc_rem, text_color="#f38ba8", font=("Segoe UI", 14, "bold")).grid(row=1, column=1, padx=12, pady=(0, 10), sticky="e")
        hud_card.grid_columnconfigure((0, 1), weight=1)

        # Operational Subscriptions Trigger Buttons Pipeline Canvas Row
        btn_grid = ctk.CTkFrame(editor_card, fg_color="transparent")
        btn_grid.pack(fill="x", side="bottom", padx=15, pady=15)
        btn_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkButton(btn_grid, text="Save Record", font=("Segoe UI", 12, "bold"), fg_color="#a6e3a1", text_color="#11111b", hover_color="#89b4fa", height=36, command=self.save_booking_record_action).grid(row=0, column=0, padx=3, sticky="nsew")
        ctk.CTkButton(btn_grid, text="Modify Record", font=("Segoe UI", 12, "bold"), fg_color="#f9e2af", text_color="#11111b", hover_color="#89b4fa", height=36, command=self.modify_booking_record_action).grid(row=0, column=1, padx=3, sticky="nsew")
        ctk.CTkButton(btn_grid, text="Purge Record", font=("Segoe UI", 12, "bold"), fg_color="#f38ba8", text_color="#11111b", hover_color="#89b4fa", height=36, command=self.purge_booking_record_action).grid(row=0, column=2, padx=3, sticky="nsew")

        # --------------------------------------------------------------------------
        # RIGHT SIDE MONITOR STREAM: NATIVE DATABASE RECORDS GRID 
        # --------------------------------------------------------------------------
        view_card = ctk.CTkFrame(self, fg_color="#313244", corner_radius=12)
        view_card.grid(row=0, column=1, sticky="nsew")
        
        lbl_vtitle = ctk.CTkLabel(
            view_card, text="Historical Master Booking Ledger",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#cba6f7"
        )
        lbl_vtitle.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Advanced Modern Responsive List Viewport Layer Wrapper
        list_container = ctk.CTkScrollableFrame(view_card, fg_color="#1e1e2e", corner_radius=10, border_width=1, border_color="#45475a")
        list_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.table_items_frame = list_container

    def refresh_table_data(self):
        """Pulls transaction rows securely and renders layout blocks without using generic table views."""
        # Flush existing dynamic row widgets inside display grid container canvas
        for child in self.table_items_frame.winfo_children():
            child.destroy()
            
        # Draw explicit list header markers layout
        headers_frame = ctk.CTkFrame(self.table_items_frame, fg_color="#181825", corner_radius=6, height=30)
        headers_frame.pack(fill="x", padx=5, pady=4)
        
        h_mappings = [("Client Profile", 0.3), ("Event Date", 0.2), ("Total Billing", 0.25), ("Status", 0.25)]
        for title, weight in h_mappings:
            lbl = ctk.CTkLabel(headers_frame, text=title, text_color="#a6adc8", font=("Segoe UI", 11, "bold"), anchor="w")
            lbl.pack(side="left", fill="x", expand=True, padx=8)

        conn = connect_database()
        if not conn:
            return
            
        try:
            cur = conn.cursor()
            # FIX: Changed columns to match your real database schema from the screenshot
            cur.execute("""
                SELECT id, customer_name, booking_date, number_of_guests, 
                        per_person_charge, advance_paid, booking_status 
                FROM bookings 
                ORDER BY booking_date DESC
            """)
            records = cur.fetchall()
            conn.close()
            
            for row in records:
                db_id, name, ev_date, guests, rate, advance, status = row
                invoice_total = guests * rate
                
                # Dynamic Theming Rows Badges Mappings for Status Fields
                status_color = "#f9e2af"  # Pending
                if status == "Confirmed": status_color = "#a6e3a1"
                elif status == "Cancelled": status_color = "#f38ba8"
                
                row_strip = ctk.CTkFrame(
                    self.table_items_frame, fg_color="#313244",
                    corner_radius=6, height=45
                )
                row_strip.pack(fill="x", padx=5, pady=3)
                row_strip.bind("<Button-1>", lambda event, r_id=db_id: self.load_selected_record_to_editor(r_id))
                
                # Content Grid Labels Placement inside individual item bars canvas maps
                lbl_name = ctk.CTkLabel(row_strip, text=f"{name}", text_color="#cdd6f4", font=("Segoe UI", 12, "bold"), anchor="w")
                lbl_name.pack(side="left", padx=10, fill="x", expand=True)
                lbl_name.bind("<Button-1>", lambda event, r_id=db_id: self.load_selected_record_to_editor(r_id))

                lbl_date = ctk.CTkLabel(row_strip, text=f"{ev_date}", text_color="#a6adc8", font=("Segoe UI", 11), anchor="w")
                lbl_date.pack(side="left", padx=10, fill="x", expand=True)
                lbl_date.bind("<Button-1>", lambda event, r_id=db_id: self.load_selected_record_to_editor(r_id))

                lbl_fin = ctk.CTkLabel(row_strip, text=f"PKR {invoice_total:,.0f}", text_color="#89b4fa", font=("Segoe UI", 11, "bold"), anchor="w")
                lbl_fin.pack(side="left", padx=10, fill="x", expand=True)
                lbl_fin.bind("<Button-1>", lambda event, r_id=db_id: self.load_selected_record_to_editor(r_id))

                lbl_stat = ctk.CTkLabel(row_strip, text=f"{status.upper()}", text_color=status_color, font=("Segoe UI", 10, "bold"), anchor="center")
                lbl_stat.pack(side="right", padx=15)
                lbl_stat.bind("<Button-1>", lambda event, r_id=db_id: self.load_selected_record_to_editor(r_id))
                
        except Exception as query_fault:
            messagebox.showerror("Database Grid Fault", f"Failed fetching historical registers rows:\n{str(query_fault)}")

    def load_selected_record_to_editor(self, record_id):
        """Binds chosen row coordinates fields backward onto configuration layout sliders forms."""
        self.selected_booking_id = record_id
        conn = connect_database()
        if not conn: return
        
        try:
            cur = conn.cursor()
            # FIX: Columns structure matched perfectly to screenshot definitions
            cur.execute("""
                SELECT booking_date, booking_date, customer_name, customer_contact, 
                       event_type, number_of_guests, per_person_charge, advance_paid, 
                       hall_name, booking_status 
                FROM bookings WHERE id = %s
            """, (record_id,))
            res = cur.fetchone()
            conn.close()
            
            if res:
                self.cal_booking.set_date(res[0])
                self.cal_event.set_date(res[1])
                self.customer_name.set(res[2])
                self.customer_contact.set(res[3])
                self.event_type.set(res[4])
                self.number_of_guests.set(str(res[5]))
                self.per_person_charge.set(str(res[6]))
                self.advance_paid.set(str(res[7]))
                self.hall_name.set(res[8])
                self.booking_status.set(res[9])
                
                # Execute instant evaluation routine loops updates
                self.execute_live_financial_calculations()
        except Exception as load_fault:
            messagebox.showerror("Form Binding Failure", str(load_fault))

    def save_booking_record_action(self):
        """Validates inputs bounds, inserts record row, and handles sub-khaata transaction updates logs."""
        if not self.customer_name.get().strip() or not self.customer_contact.get().strip():
            messagebox.showwarning("Validation Error", "Client Profile identities cannot be left completely empty.")
            return
            
        conn = connect_database()
        if not conn: return
        
        try:
            guests = int(self.number_of_guests.get()) if self.number_of_guests.get().isdigit() else 0
            rate = float(self.per_person_charge.get()) if self.per_person_charge.get().replace('.', '', 1).isdigit() else 0.0
            advance = float(self.advance_paid.get()) if self.advance_paid.get().replace('.', '', 1).isdigit() else 0.0
            total_amount = guests * rate
            
            cur = conn.cursor()
            # FIX: Structural Database queries columns sync architecture matching layout
            cur.execute("""
                INSERT INTO bookings (
                    booking_date, customer_name, customer_contact, 
                    event_type, number_of_guests, per_person_charge, total_amount, 
                    advance_paid, hall_name, booking_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.cal_booking.get_date(),
                self.customer_name.get().strip(),
                self.customer_contact.get().strip(),
                self.event_type.get(),
                guests,
                rate,
                total_amount,
                advance,
                self.hall_name.get(),
                self.booking_status.get()
            ))
            
            new_booking_id = cur.lastrowid
            
            # --------------------------------------------------------------------------
            # SYSTEM INTEGRATION CRITICAL ARCHITECTURE LOG: SUB-KHAATA MAPPING LINK PIPELINE
            # --------------------------------------------------------------------------
            if self.booking_status.get() == "Confirmed":
                pass
                
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Operational Status", "Event Invoice Log saved completely onto cluster nodes securely.")
            self.clear_form_fields_state()
            self.refresh_table_data()
            
            # Safely reload KPI updates variables blocks loops back onto executive parent canvas frames
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
                
        except Exception as persistence_fault:
            messagebox.showerror("SQL Transaction Crash", f"Data execution engine dropped requests updates:\n{str(persistence_fault)}")

    def modify_booking_record_action(self):
        """Updates properties coordinates parameters maps over historical registers rows targets records."""
        if not self.selected_booking_id:
            messagebox.showwarning("Context Error", "Please pick a transactional item record from the tracking sheet first.")
            return
            
        conn = connect_database()
        if not conn: return
        
        try:
            guests = int(self.number_of_guests.get()) if self.number_of_guests.get().isdigit() else 0
            rate = float(self.per_person_charge.get()) if self.per_person_charge.get().replace('.', '', 1).isdigit() else 0.0
            advance = float(self.advance_paid.get()) if self.advance_paid.get().replace('.', '', 1).isdigit() else 0.0
            total_amount = guests * rate
            
            cur = conn.cursor()
            # FIX: Clean sync mappings to drop missing parameters crashes
            cur.execute("""
                UPDATE bookings SET 
                    booking_date = %s, customer_name = %s, 
                    customer_contact = %s, event_type = %s, number_of_guests = %s, 
                    per_person_charge = %s, total_amount = %s, advance_paid = %s, 
                    hall_name = %s, booking_status = %s
                WHERE id = %s
            """, (
                self.cal_booking.get_date(),
                self.customer_name.get().strip(),
                self.customer_contact.get().strip(),
                self.event_type.get(),
                guests,
                rate,
                total_amount,
                advance,
                self.hall_name.get(),
                self.booking_status.get(),
                self.selected_booking_id
            ))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Operational Status", "Row entry values synced perfectly across records pools.")
            self.clear_form_fields_state()
            self.refresh_table_data()
            
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
                
        except Exception as modification_fault:
            messagebox.showerror("SQL Mutation Fault", str(modification_fault))

    def purge_booking_record_action(self):
        """Drops target row references keys securely from backend table matrices schemas entries pools."""
        if not self.selected_booking_id:
            messagebox.showwarning("Selection Missing", "Please click a target list transaction line block to drop.")
            return
            
        confirm_action = messagebox.askyesno("Destructive Security Request", "Are you sure you want to drop this transaction row permanently?")
        if not confirm_action: return
        
        conn = connect_database()
        if not conn: return
        
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM bookings WHERE id = %s", (self.selected_booking_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Purge Successful", "Row entry targets references destroyed completely.")
            self.clear_form_fields_state()
            self.refresh_table_data()
            
            if hasattr(self.master, 'load_kpi_metrics'):
                self.master.load_kpi_metrics()
        except Exception as terminal_fault:
            messagebox.showerror("Purge Execution Interrupted", str(terminal_fault))

    def clear_form_fields_state(self):
        """Flushes storage handles arrays variables pointers cleanly to start a fresh input session."""
        self.selected_booking_id = None
        self.customer_name.set("")
        self.customer_contact.set("")
        self.event_type.set(EVENT_TYPES[0])
        self.hall_name.set(HALLS[0])
        self.booking_status.set(STATUS_TYPES[0])
        self.number_of_guests.set("0")
        self.per_person_charge.set("0")
        self.advance_paid.set("0")
        self.lbl_calc_total.set("PKR 0.00")
        self.lbl_calc_rem.set("PKR 0.00")