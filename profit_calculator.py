# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import date, timedelta
import csv

from db.connection import connect_database

# ---------- Helper ----------
def safe_float(x, default=0.0):
    try:
        return float(x or 0)
    except Exception:
        return default

class ProfitCalculator:
    """
    Advanced Profit Calculator
    - Mode 1: Per-Event (select booking) -> auto revenue, costs window, net profit
    - Mode 2: Date Range summary (many bookings)
    - Cost sources supported (if tables exist):
        * expenses (amount)
        * khaata_karyana (price)
        * khaata_chicken (price)
        * khaata_meat (price)
        * khaata_milk_dairy (price)
        * khaata_fruits_vegetables (total_cost OR price, whichever exists)
        * temporary_employees (total_pay)  [optional; if you add later]
    - Export CSV
    """

    def __init__(self, root: tk.Toplevel):
        self.root = root
        self.root.title("🧮 Profit Calculator")
        self.root.geometry("1250x760")
        self.root.configure(bg="white")

        self.mode = tk.StringVar(value="per_event")
        self.notes_var = tk.StringVar(value="")
        self.window_days = tk.IntVar(value=0)  # event-date centered window: [event - d, event + d]
        self.include_pending = tk.BooleanVar(value=True)  # include pending balances as revenue? (no—only total; outstanding shown separately)

        # Filters (Per-event)
        self.selected_booking_id = tk.StringVar()
        self.from_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.to_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))

        # cost toggles
        self.cost_sources = {
            "expenses": tk.BooleanVar(value=True),
            "khaata_karyana": tk.BooleanVar(value=True),
            "khaata_chicken": tk.BooleanVar(value=True),
            "khaata_meat": tk.BooleanVar(value=True),
            "khaata_milk_dairy": tk.BooleanVar(value=True),
            "khaata_fruits_vegetables": tk.BooleanVar(value=True),
            "temporary_employees": tk.BooleanVar(value=True),  # optional
        }

        self._build_header()
        self._build_filters()
        self._build_cards()
        self._build_breakdown()
        self._load_bookings()

    # ---------- UI ----------
    def _build_header(self):
        bar = tk.Frame(self.root, bg="#0d6efd", padx=12, pady=10)
        bar.pack(fill="x")
        tk.Label(bar, text="Profit & Loss Calculator", bg="#0d6efd", fg="white",
                 font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Button(bar, text="↻ Refresh Bookings", command=self._load_bookings).pack(side="right", padx=4)

    def _build_filters(self):
        wrap = tk.Frame(self.root, bg="white")
        wrap.pack(fill="x", padx=12, pady=10)

        # Mode toggle
        mode_box = tk.LabelFrame(wrap, text="Mode", bg="white")
        mode_box.pack(side="left", fill="y", padx=(0, 10))
        ttk.Radiobutton(mode_box, text="Per-Event", variable=self.mode, value="per_event",
                        command=self._toggle_mode).pack(anchor="w", padx=8, pady=4)
        ttk.Radiobutton(mode_box, text="Date Range", variable=self.mode, value="date_range",
                        command=self._toggle_mode).pack(anchor="w", padx=8, pady=4)

        # Per-event box
        self.event_box = tk.LabelFrame(wrap, text="Per-Event Filters", bg="white")
        self.event_box.pack(side="left", fill="x", expand=True, padx=(0, 10))

        tk.Label(self.event_box, text="Booking:", bg="white").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.booking_cb = ttk.Combobox(self.event_box, textvariable=self.selected_booking_id, state="readonly", width=46)
        self.booking_cb.grid(row=0, column=1, sticky="w", padx=6, pady=6)

        tk.Label(self.event_box, text="± Days Window:", bg="white").grid(row=0, column=2, sticky="e", padx=6)
        self.window_sp = ttk.Spinbox(self.event_box, from_=0, to=30, textvariable=self.window_days, width=6)
        self.window_sp.grid(row=0, column=3, sticky="w", padx=6)

        # Date-range box
        self.range_box = tk.LabelFrame(wrap, text="Date Range Filters", bg="white")
        self.range_box.pack(side="left", fill="x", expand=True)

        tk.Label(self.range_box, text="From:", bg="white").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.from_de = DateEntry(self.range_box, date_pattern="yyyy-mm-dd", width=14)
        self.from_de.set_date(date(date.today().year, 1, 1))
        self.from_de.grid(row=0, column=1, sticky="w")

        tk.Label(self.range_box, text="To:", bg="white").grid(row=0, column=2, sticky="e", padx=6)
        self.to_de = DateEntry(self.range_box, date_pattern="yyyy-mm-dd", width=14)
        self.to_de.set_date(date.today())
        self.to_de.grid(row=0, column=3, sticky="w")

        # Cost sources
        costs_box = tk.LabelFrame(self.root, text="Included Cost Sources", bg="white")
        costs_box.pack(fill="x", padx=12, pady=(0, 10))
        r1 = tk.Frame(costs_box, bg="white"); r1.pack(fill="x")
        r2 = tk.Frame(costs_box, bg="white"); r2.pack(fill="x")
        keys = list(self.cost_sources.keys())
        half = (len(keys) + 1) // 2
        for k in keys[:half]:
            ttk.Checkbutton(r1, text=k.replace("_", " ").title(), variable=self.cost_sources[k]).pack(side="left", padx=10, pady=6)
        for k in keys[half:]:
            ttk.Checkbutton(r2, text=k.replace("_", " ").title(), variable=self.cost_sources[k]).pack(side="left", padx=10, pady=6)

        # Action buttons
        act = tk.Frame(self.root, bg="white")
        act.pack(fill="x", padx=12, pady=(0, 10))
        ttk.Button(act, text="🔍 Calculate", command=self.calculate).pack(side="left")
        ttk.Button(act, text="💾 Export CSV", command=self.export_csv).pack(side="left", padx=6)
        ttk.Button(act, text="🧹 Clear", command=self._clear_results).pack(side="left", padx=6)

        self._toggle_mode()

    def _build_cards(self):
        self.cards = tk.Frame(self.root, bg="white")
        self.cards.pack(fill="x", padx=12, pady=6)

        def make_card(parent, title):
            f = tk.Frame(parent, bg="#f9fafb", highlightbackground="#e5e7eb", highlightthickness=1, padx=16, pady=12)
            tk.Label(f, text=title, bg="#f9fafb", fg="#6b7280", font=("Segoe UI", 10, "bold")).pack(anchor="w")
            val = tk.StringVar(value="0.00")
            tk.Label(f, textvariable=val, bg="#f9fafb", fg="#111827", font=("Segoe UI", 16, "bold")).pack(anchor="w")
            return f, val

        self.card_frames = []
        self.val_revenue = None
        titles = ["Total Revenue (Rs)", "Advance Received (Rs)", "Outstanding (Rs)", "Total Costs (Rs)", "Net Profit (Rs)", "Margin %"]
        self.card_vars = []
        for t in titles:
            fr, var = make_card(self.cards, t)
            fr.pack(side="left", padx=8, pady=6, fill="x", expand=True)
            self.card_frames.append(fr)
            self.card_vars.append(var)

    def _build_breakdown(self):
        box = tk.LabelFrame(self.root, text="Breakdown", bg="white")
        box.pack(fill="both", expand=True, padx=12, pady=8)

        cols = ("type", "ref", "date", "desc", "amount")
        self.tree = ttk.Treeview(box, columns=cols, show="headings", height=16)
        for c, h in zip(cols, ["Source", "Ref / ID", "Date", "Description", "Amount (Rs)"]):
            self.tree.heading(c, text=h)
        widths = [140, 120, 110, 600, 120]
        for c, w in zip(cols, widths):
            self.tree.column(c, width=w, anchor="center" if c in ("type", "ref", "date", "amount") else "w")
        self.tree.pack(fill="both", expand=True)

        # info label
        self.info_lbl = tk.Label(self.root, text="", bg="white", fg="#6b7280", anchor="w")
        self.info_lbl.pack(fill="x", padx=12, pady=(0, 10))

    # ---------- Data ----------
    def _load_bookings(self):
        try:
            conn = connect_database()
            cur = conn.cursor()
            cur.execute("""
                SELECT booking_id, event_date, client_name, guest_count, per_person_rate, total_amount, advance_paid, balance_amount
                FROM bookings
                ORDER BY event_date DESC
            """)
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            rows = []
            messagebox.showwarning("Bookings", f"Could not load bookings:\n{e}")

        display = []
        self._bookings_index = {}  # booking_id -> dict
        for r in rows:
            (bid, ev_date, client, guests, rate, total, adv, bal) = r
            label = f"#{bid} | {ev_date} | {client} | Guests:{guests} | Total:{total}"
            display.append(label)
            self._bookings_index[str(bid)] = {
                "booking_id": bid, "event_date": ev_date, "client_name": client,
                "guest_count": guests, "rate": rate, "total": total, "advance": adv, "balance": bal
            }
        # Map display -> id using first token after '#'
        self.booking_cb["values"] = display
        if display:
            self.booking_cb.current(0)
            first = display[0]
            self.selected_booking_id.set(first.split("|")[0].strip().lstrip("#"))

    def _toggle_mode(self):
        if self.mode.get() == "per_event":
            for w in self.event_box.winfo_children(): w.configure(state="normal")
            for w in self.range_box.winfo_children(): w.configure(state="disabled")
        else:
            for w in self.event_box.winfo_children(): w.configure(state="disabled")
            for w in self.range_box.winfo_children(): w.configure(state="normal")

    def _clear_results(self):
        for var in self.card_vars:
            var.set("0.00")
        for r in self.tree.get_children():
            self.tree.delete(r)
        self.info_lbl.config(text="")

    # ---------- Calculation ----------
    def calculate(self):
        self._clear_results()
        try:
            if self.mode.get() == "per_event":
                self._calc_per_event()
            else:
                self._calc_date_range()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- costs helpers ---
    def _sum_expenses(self, start_date, end_date, add_rows):
        total = 0.0
        conn = connect_database()
        cur = conn.cursor()
        try:
            cur.execute("SELECT expense_id, date, expense_type, description, amount FROM expenses WHERE date BETWEEN %s AND %s",
                        (start_date, end_date))
            for (eid, d, et, desc, amt) in cur.fetchall():
                amt = safe_float(amt)
                total += amt
                if add_rows:
                    self.tree.insert("", "end", values=("Expense", eid, d, f"{et} - {desc or ''}", f"{amt:,.2f}"))
        except Exception:
            # expenses table may not exist yet
            pass
        conn.close()
        return total

    def _sum_simple_khaata(self, table, date_field, price_field, start_date, end_date, add_rows, display_name=None, extra_cols=None):
        # price_field can be a stored total or unit price; here we simply sum price_field
        total = 0.0
        conn = connect_database(); cur = conn.cursor()
        try:
            cols = "id, {df}, {pf}".format(df=date_field, pf=price_field)
            desc_cols = []
            if extra_cols:
                cols += ", " + ", ".join(extra_cols)
                desc_cols = extra_cols
            cur.execute(f"SELECT {cols} FROM {table} WHERE {date_field} BETWEEN %s AND %s", (start_date, end_date))
            for row in cur.fetchall():
                rec_id = row[0]; d = row[1]; price = safe_float(row[2])
                total += price
                if add_rows:
                    desc = ""
                    if desc_cols:
                        extras = row[3:]
                        desc_parts = [str(x) for x in extras if x not in (None, "")]
                        desc = " | ".join(desc_parts)
                    self.tree.insert("", "end", values=(display_name or table, rec_id, d, desc, f"{price:,.2f}"))
        except Exception:
            pass
        conn.close()
        return total

    # --- modes ---
    def _calc_per_event(self):
        display_val = self.booking_cb.get().strip()
        if not display_val:
            messagebox.showwarning("Select", "Please select a booking first.")
            return

        # get booking_id from label (starts with '#ID')
        bid = display_val.split("|")[0].strip().lstrip("#")
        conn = connect_database()
        cur = conn.cursor()
        cur.execute("""
            SELECT booking_id, event_date, client_name, guest_count, per_person_rate, total_amount, advance_paid, balance_amount
            FROM bookings WHERE booking_id=%s
        """, (bid,))
        row = cur.fetchone()
        conn.close()
        if not row:
            messagebox.showerror("Not found", "Selected booking not found.")
            return

        booking_id, ev_date, client, guests, rate, total, adv, bal = row

        # revenue cards (total/advance/balance)
        total = safe_float(total)
        adv = safe_float(adv)
        bal = safe_float(bal)

        # cost window
        d = self.window_days.get()
        start_date = (ev_date - timedelta(days=d)).strftime("%Y-%m-%d")
        end_date = (ev_date + timedelta(days=d)).strftime("%Y-%m-%d")

        # aggregate costs
        costs = 0.0
        # expenses
        if self.cost_sources["expenses"].get():
            costs += self._sum_expenses(start_date, end_date, add_rows=True)

        # khaata tables (sum price/total_cost)
        if self.cost_sources["khaata_karyana"].get():
            costs += self._sum_simple_khaata("khaata_karyana", "purchase_date", "price",
                                             start_date, end_date, True, "Karyana", ["item_name", "quantity", "unit", "supplier"])
        if self.cost_sources["khaata_chicken"].get():
            costs += self._sum_simple_khaata("khaata_chicken", "purchase_date", "price",
                                             start_date, end_date, True, "Chicken", ["item_name", "quantity", "unit", "supplier"])
        if self.cost_sources["khaata_meat"].get():
            costs += self._sum_simple_khaata("khaata_meat", "purchase_date", "price",
                                             start_date, end_date, True, "Meat", ["item_name", "quantity", "unit", "supplier"])
        if self.cost_sources["khaata_milk_dairy"].get():
            costs += self._sum_simple_khaata("khaata_milk_dairy", "purchase_date", "price",
                                             start_date, end_date, True, "Milk & Dairy", ["item_name", "quantity", "unit", "supplier"])
        if self.cost_sources["khaata_fruits_vegetables"].get():
            # this table (advanced) may have total_cost or price; try total_cost first
            subtotal = self._sum_simple_khaata("khaata_fruits_vegetables", "purchase_date", "total_cost",
                                               start_date, end_date, True, "Fruits & Veg", ["item_name", "quantity", "unit", "supplier"])
            if subtotal == 0.0:
                subtotal = self._sum_simple_khaata("khaata_fruits_vegetables", "purchase_date", "price",
                                                   start_date, end_date, True, "Fruits & Veg", ["item_name", "quantity", "unit", "supplier"])
            costs += subtotal

        if self.cost_sources["temporary_employees"].get():
            # Optional table: temporary_employees (event_date, role, person_name, qty, rate, total_pay)
            costs += self._sum_simple_khaata("temporary_employees", "work_date", "total_pay",
                                             start_date, end_date, True, "Temp Staff", ["role", "person_name", "qty", "rate"])

        # results
        net = total - costs
        margin = (net / total * 100.0) if total > 0 else 0.0

        self.card_vars[0].set(f"{total:,.2f}")      # revenue
        self.card_vars[1].set(f"{adv:,.2f}")        # advance
        self.card_vars[2].set(f"{bal:,.2f}")        # outstanding
        self.card_vars[3].set(f"{costs:,.2f}")      # total costs
        self.card_vars[4].set(f"{net:,.2f}")        # net profit
        self.card_vars[5].set(f"{margin:,.2f}%")    # margin

        self.info_lbl.config(text=f"Booking #{booking_id} | Event Date: {ev_date} | Client: {client} | Guests: {guests}")

    def _calc_date_range(self):
        start_date = self.from_de.get_date().strftime("%Y-%m-%d")
        end_date = self.to_de.get_date().strftime("%Y-%m-%d")

        # Revenue from bookings in range (event_date)
        total_revenue = 0.0
        total_advance = 0.0
        total_balance = 0.0

        conn = connect_database()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT booking_id, event_date, client_name, total_amount, advance_paid, balance_amount
                FROM bookings
                WHERE event_date BETWEEN %s AND %s
                ORDER BY event_date
            """, (start_date, end_date))
            for (bid, evd, client, total, adv, bal) in cur.fetchall():
                total = safe_float(total); adv = safe_float(adv); bal = safe_float(bal)
                total_revenue += total
                total_advance += adv
                total_balance += bal
                # add a line into breakdown (as info)
                self.tree.insert("", "end", values=("Booking", bid, evd, f"{client}", f"{total:,.2f}"))
        except Exception:
            pass
        conn.close()

        # Costs
        costs = 0.0
        if self.cost_sources["expenses"].get():
            costs += self._sum_expenses(start_date, end_date, add_rows=True)
        if self.cost_sources["khaata_karyana"].get():
            costs += self._sum_simple_khaata("khaata_karyana", "purchase_date", "price",
                                             start_date, end_date, True, "Karyana", ["item_name", "quantity", "unit", "supplier"])
        if self.cost_sources["khaata_chicken"].get():
            costs += self._sum_simple_khaata("khaata_chicken", "purchase_date", "price",
                                             start_date, end_date, True, "Chicken", ["item_name", "quantity", "unit", "supplier"])
        if self.cost_sources["khaata_meat"].get():
            costs += self._sum_simple_khaata("khaata_meat", "purchase_date", "price",
                                             start_date, end_date, True, "Meat", ["item_name", "quantity", "unit", "supplier"])
        if self.cost_sources["khaata_milk_dairy"].get():
            costs += self._sum_simple_khaata("khaata_milk_dairy", "purchase_date", "price",
                                             start_date, end_date, True, "Milk & Dairy", ["item_name", "quantity", "unit", "supplier"])
        if self.cost_sources["khaata_fruits_vegetables"].get():
            subtotal = self._sum_simple_khaata("khaata_fruits_vegetables", "purchase_date", "total_cost",
                                               start_date, end_date, True, "Fruits & Veg", ["item_name", "quantity", "unit", "supplier"])
            if subtotal == 0.0:
                subtotal = self._sum_simple_khaata("khaata_fruits_vegetables", "purchase_date", "price",
                                                   start_date, end_date, True, "Fruits & Veg", ["item_name", "quantity", "unit", "supplier"])
            costs += subtotal
        if self.cost_sources["temporary_employees"].get():
            costs += self._sum_simple_khaata("temporary_employees", "work_date", "total_pay",
                                             start_date, end_date, True, "Temp Staff", ["role", "person_name", "qty", "rate"])

        net = total_revenue - costs
        margin = (net / total_revenue * 100.0) if total_revenue > 0 else 0.0

        self.card_vars[0].set(f"{total_revenue:,.2f}")
        self.card_vars[1].set(f"{total_advance:,.2f}")
        self.card_vars[2].set(f"{total_balance:,.2f}")
        self.card_vars[3].set(f"{costs:,.2f}")
        self.card_vars[4].set(f"{net:,.2f}")
        self.card_vars[5].set(f"{margin:,.2f}%")

        self.info_lbl.config(text=f"Range: {start_date} → {end_date}")

    # ---------- Export ----------
    def export_csv(self):
        if not self.tree.get_children():
            messagebox.showwarning("Empty", "Nothing to export. Calculate first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="profit_breakdown.csv"
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Source", "Ref/ID", "Date", "Description", "Amount (Rs)"])
            for iid in self.tree.get_children():
                writer.writerow(self.tree.item(iid)["values"])
        messagebox.showinfo("Export", f"Saved:\n{path}")
