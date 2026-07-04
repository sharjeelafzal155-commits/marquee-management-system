# -*- coding: utf-8 -*-
# Advanced Employees Management + Advance Salary System
# Save as: forms/employees_advanced_form.py

import os
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import mysql.connector
from datetime import date, datetime
import csv

# ------------------- DB CONNECT -------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="marquee_management"
    )

# ------------------- DB INIT (SAFE) -------------------
def ensure_tables():
    ddl_employees = """
    CREATE TABLE IF NOT EXISTS employees (
        employee_id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(100) NOT NULL,
        role VARCHAR(50) NOT NULL,
        contact_number VARCHAR(20),
        cnic VARCHAR(20),
        address TEXT,
        join_date DATE,
        contract_type ENUM('Permanent','Part-time','Seasonal') DEFAULT 'Permanent',
        shift ENUM('Morning','Evening','Night','Full Day') DEFAULT 'Full Day',
        status ENUM('Active','On Leave','Resigned') DEFAULT 'Active',
        salary_type ENUM('Monthly','Daily','Per Event','Hourly') DEFAULT 'Monthly',
        salary_amount DECIMAL(10,2) DEFAULT 0,
        payment_method ENUM('Cash','Bank Transfer','JazzCash','EasyPaisa') DEFAULT 'Cash',
        bank_account VARCHAR(50),
        cnic_attachment VARCHAR(255),
        resume_attachment VARCHAR(255),
        contract_attachment VARCHAR(255),
        remarks TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    ddl_advances = """
    CREATE TABLE IF NOT EXISTS employee_advances (
        id INT AUTO_INCREMENT PRIMARY KEY,
        employee_id INT NOT NULL,
        advance_date DATE NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        recovered_amount DECIMAL(10,2) DEFAULT 0,
        purpose VARCHAR(200),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
    )
    """

    con = connect_db()
    cur = con.cursor()
    cur.execute(ddl_employees)
    cur.execute(ddl_advances)
    con.commit()
    con.close()

# ------------------- UTIL -------------------
ROLES = ["Manager", "Waiter", "Cook", "Cleaner", "Security", "Cashier", "Store Keeper", "BBQ Master", "Dish Washer", "Roti Maker", "Helper"]
CONTRACTS = ["Permanent", "Part-time", "Seasonal"]
SHIFTS = ["Morning", "Evening", "Night", "Full Day"]
STATUSES = ["Active", "On Leave", "Resigned"]
SAL_TYPES = ["Monthly", "Daily", "Per Event", "Hourly"]
PAY_METHODS = ["Cash", "Bank Transfer", "JazzCash", "EasyPaisa"]

def to_float(val, default=0.0):
    try:
        return float(val)
    except:
        return default

# ------------------- MAIN FORM -------------------
class EmployeesAdvancedForm:
    def __init__(self, root):
        ensure_tables()

        self.root = root
        self.root.title("👥 Employees Management (Advanced)")
        self.root.geometry("1200x700")
        self.root.configure(bg="white")

        # ---- Vars ----
        self.employee_id = None
        self.v_full_name = StringVar()
        self.v_role = StringVar()
        self.v_contact = StringVar()
        self.v_cnic = StringVar()
        self.v_address = StringVar()
        self.v_join_date = StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.v_contract = StringVar(value="Permanent")
        self.v_shift = StringVar(value="Full Day")
        self.v_status = StringVar(value="Active")
        self.v_salary_type = StringVar(value="Monthly")
        self.v_salary_amount = StringVar(value="0")
        self.v_payment_method = StringVar(value="Cash")
        self.v_bank_account = StringVar()
        self.v_cnic_path = StringVar()
        self.v_resume_path = StringVar()
        self.v_contract_path = StringVar()
        self.v_remarks = StringVar()

        self.s_search = StringVar()
        self.f_role = StringVar(value="All")
        self.f_status = StringVar(value="All")

        # ---- Title ----
        title = Label(self.root, text="👥 Employees Management (Advanced) — with Advance Salary",
                      font=("Segoe UI", 18, "bold"), bg="#1E3A8A", fg="white", pady=10)
        title.pack(fill=X)

        # ---- Top Toolbar (Search/Filters/Export) ----
        toolbar = Frame(self.root, bg="white")
        toolbar.pack(fill=X, padx=10, pady=(10, 5))

        Label(toolbar, text="Search:", bg="white").pack(side=LEFT, padx=(5, 2))
        Entry(toolbar, textvariable=self.s_search, width=30).pack(side=LEFT, padx=(0, 10))
        Button(toolbar, text="🔍 Go", command=self.apply_filters).pack(side=LEFT)

        Label(toolbar, text="  Role:", bg="white").pack(side=LEFT, padx=(15, 2))
        role_cb = ttk.Combobox(toolbar, values=["All"] + ROLES, textvariable=self.f_role, state="readonly", width=18)
        role_cb.pack(side=LEFT)

        Label(toolbar, text="  Status:", bg="white").pack(side=LEFT, padx=(15, 2))
        status_cb = ttk.Combobox(toolbar, values=["All"] + STATUSES, textvariable=self.f_status, state="readonly", width=18)
        status_cb.pack(side=LEFT)

        Button(toolbar, text="♻ Reset", command=self.reset_filters).pack(side=LEFT, padx=10)
        Button(toolbar, text="⬇ Export CSV", command=self.export_csv).pack(side=RIGHT, padx=5)

        # ---- Main Split: Left (Form) / Right (Table) ----
        body = Frame(self.root, bg="white")
        body.pack(fill=BOTH, expand=True, padx=10, pady=5)

        left = Frame(body, bg="white")
        left.pack(side=LEFT, fill=Y, padx=(0, 10))

        right = Frame(body, bg="white")
        right.pack(side=RIGHT, fill=BOTH, expand=True)

        # ---- Left Form ----
        form = LabelFrame(left, text="Employee Details", bg="white", padx=10, pady=10)
        form.pack(fill=Y)

        # row 0
        Label(form, text="Full Name *", bg="white").grid(row=0, column=0, sticky="w")
        Entry(form, textvariable=self.v_full_name, width=28).grid(row=0, column=1, padx=5, pady=4)

        Label(form, text="Role *", bg="white").grid(row=0, column=2, sticky="w")
        ttk.Combobox(form, values=ROLES, textvariable=self.v_role, state="readonly", width=24).grid(row=0, column=3, padx=5, pady=4)

        # row 1
        Label(form, text="Contact", bg="white").grid(row=1, column=0, sticky="w")
        Entry(form, textvariable=self.v_contact, width=28).grid(row=1, column=1, padx=5, pady=4)

        Label(form, text="CNIC", bg="white").grid(row=1, column=2, sticky="w")
        Entry(form, textvariable=self.v_cnic, width=24).grid(row=1, column=3, padx=5, pady=4)

        # row 2
        Label(form, text="Address", bg="white").grid(row=2, column=0, sticky="w")
        Entry(form, textvariable=self.v_address, width=28).grid(row=2, column=1, padx=5, pady=4)

        Label(form, text="Join Date", bg="white").grid(row=2, column=2, sticky="w")
        self.join_picker = DateEntry(form, textvariable=self.v_join_date, width=22, date_pattern="yyyy-mm-dd")
        self.join_picker.grid(row=2, column=3, padx=5, pady=4)

        # row 3
        Label(form, text="Contract", bg="white").grid(row=3, column=0, sticky="w")
        ttk.Combobox(form, values=CONTRACTS, textvariable=self.v_contract, state="readonly", width=26).grid(row=3, column=1, padx=5, pady=4)

        Label(form, text="Shift", bg="white").grid(row=3, column=2, sticky="w")
        ttk.Combobox(form, values=SHIFTS, textvariable=self.v_shift, state="readonly", width=24).grid(row=3, column=3, padx=5, pady=4)

        # row 4
        Label(form, text="Status", bg="white").grid(row=4, column=0, sticky="w")
        ttk.Combobox(form, values=STATUSES, textvariable=self.v_status, state="readonly", width=26).grid(row=4, column=1, padx=5, pady=4)

        Label(form, text="Salary Type", bg="white").grid(row=4, column=2, sticky="w")
        ttk.Combobox(form, values=SAL_TYPES, textvariable=self.v_salary_type, state="readonly", width=24).grid(row=4, column=3, padx=5, pady=4)

        # row 5
        Label(form, text="Salary Amount", bg="white").grid(row=5, column=0, sticky="w")
        Entry(form, textvariable=self.v_salary_amount, width=28).grid(row=5, column=1, padx=5, pady=4)

        Label(form, text="Payment Method", bg="white").grid(row=5, column=2, sticky="w")
        ttk.Combobox(form, values=PAY_METHODS, textvariable=self.v_payment_method, state="readonly", width=24).grid(row=5, column=3, padx=5, pady=4)

        # row 6
        Label(form, text="Bank/Wallet", bg="white").grid(row=6, column=0, sticky="w")
        Entry(form, textvariable=self.v_bank_account, width=28).grid(row=6, column=1, padx=5, pady=4)

        Label(form, text="Remarks", bg="white").grid(row=6, column=2, sticky="w")
        Entry(form, textvariable=self.v_remarks, width=24).grid(row=6, column=3, padx=5, pady=4)

        # row 7 attachments
        Label(form, text="CNIC File", bg="white").grid(row=7, column=0, sticky="w")
        att1 = Frame(form, bg="white"); att1.grid(row=7, column=1, sticky="w")
        Entry(att1, textvariable=self.v_cnic_path, width=22).pack(side=LEFT)
        Button(att1, text="Browse", command=lambda: self.pick_file(self.v_cnic_path)).pack(side=LEFT, padx=3)

        Label(form, text="Resume", bg="white").grid(row=7, column=2, sticky="w")
        att2 = Frame(form, bg="white"); att2.grid(row=7, column=3, sticky="w")
        Entry(att2, textvariable=self.v_resume_path, width=18).pack(side=LEFT)
        Button(att2, text="Browse", command=lambda: self.pick_file(self.v_resume_path)).pack(side=LEFT, padx=3)

        Label(form, text="Contract", bg="white").grid(row=8, column=0, sticky="w")
        att3 = Frame(form, bg="white"); att3.grid(row=8, column=1, sticky="w")
        Entry(att3, textvariable=self.v_contract_path, width=22).pack(side=LEFT)
        Button(att3, text="Browse", command=lambda: self.pick_file(self.v_contract_path)).pack(side=LEFT, padx=3)

        # row 9 buttons
        btns = Frame(form, bg="white")
        btns.grid(row=9, column=0, columnspan=4, pady=(8, 0), sticky="w")
        Button(btns, text="➕ Save", bg="#1E3A8A", fg="white", width=10, command=self.save_employee).pack(side=LEFT, padx=3)
        Button(btns, text="✏ Update", bg="#0EA5E9", fg="white", width=10, command=self.update_employee).pack(side=LEFT, padx=3)
        Button(btns, text="🗑 Delete", bg="#DC2626", fg="white", width=10, command=self.delete_employee).pack(side=LEFT, padx=3)
        Button(btns, text="🧾 Advances", bg="#F59E0B", fg="white", width=12, command=self.open_advances).pack(side=LEFT, padx=3)
        Button(btns, text="🧹 Clear", command=self.clear_form).pack(side=LEFT, padx=3)

        # ---- Right Table ----
        rtop = Frame(right, bg="white"); rtop.pack(fill=X)
        self.summary_lbl = Label(rtop, text="Employees: 0 | Active: 0 | On Leave: 0 | Resigned: 0", bg="white", fg="#444", anchor="w")
        self.summary_lbl.pack(fill=X, padx=5, pady=(0, 5))

        cols = ("employee_id","full_name","role","contact_number","cnic","join_date","contract_type",
                "shift","status","salary_type","salary_amount","payment_method","bank_account","adv_outstanding")
        self.tree = ttk.Treeview(right, columns=cols, show="headings")
        self.tree.pack(fill=BOTH, expand=True)

        heads = ["ID","Name","Role","Contact","CNIC","Join Date","Contract","Shift","Status","Salary Type","Salary","Pay Method","Bank/Wallet","Advance O/S"]
        for c, h in zip(cols, heads):
            self.tree.heading(c, text=h)
        self.tree.column("employee_id", width=50, anchor="center")
        self.tree.column("full_name", width=180)
        self.tree.column("role", width=120)
        self.tree.column("contact_number", width=110)
        self.tree.column("cnic", width=110)
        self.tree.column("join_date", width=90, anchor="center")
        self.tree.column("contract_type", width=90, anchor="center")
        self.tree.column("shift", width=90, anchor="center")
        self.tree.column("status", width=90, anchor="center")
        self.tree.column("salary_type", width=90, anchor="center")
        self.tree.column("salary_amount", width=90, anchor="e")
        self.tree.column("payment_method", width=110, anchor="center")
        self.tree.column("bank_account", width=120)
        self.tree.column("adv_outstanding", width=100, anchor="e")

        self.tree.bind("<ButtonRelease-1>", self.fill_from_table)

        self.load_table()

    # ------------------- FILE PICKER -------------------
    def pick_file(self, var: StringVar):
        path = filedialog.askopenfilename(title="Select File")
        if path:
            var.set(path)

    # ------------------- CRUD -------------------
    def validate(self):
        if not self.v_full_name.get().strip():
            messagebox.showerror("Missing", "Full Name is required.")
            return False
        if not self.v_role.get().strip():
            messagebox.showerror("Missing", "Role is required.")
            return False
        # optional: salary numeric
        try:
            float(self.v_salary_amount.get() or "0")
        except:
            messagebox.showerror("Invalid", "Salary Amount must be a number.")
            return False
        return True

    def save_employee(self):
        if not self.validate(): return
        try:
            con = connect_db(); cur = con.cursor()
            cur.execute("""
                INSERT INTO employees
                (full_name, role, contact_number, cnic, address, join_date, contract_type, shift, status,
                 salary_type, salary_amount, payment_method, bank_account, cnic_attachment, resume_attachment,
                 contract_attachment, remarks)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                self.v_full_name.get(), self.v_role.get(), self.v_contact.get(), self.v_cnic.get(), self.v_address.get(),
                self.v_join_date.get(), self.v_contract.get(), self.v_shift.get(), self.v_status.get(),
                self.v_salary_type.get(), to_float(self.v_salary_amount.get()), self.v_payment_method.get(), self.v_bank_account.get(),
                self.v_cnic_path.get(), self.v_resume_path.get(), self.v_contract_path.get(), self.v_remarks.get()
            ))
            con.commit(); con.close()
            messagebox.showinfo("Saved", "Employee saved successfully.")
            self.clear_form()
            self.load_table()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def update_employee(self):
        if not self.employee_id:
            messagebox.showwarning("Select", "Select an employee from table.")
            return
        if not self.validate(): return
        try:
            con = connect_db(); cur = con.cursor()
            cur.execute("""
                UPDATE employees SET
                    full_name=%s, role=%s, contact_number=%s, cnic=%s, address=%s,
                    join_date=%s, contract_type=%s, shift=%s, status=%s,
                    salary_type=%s, salary_amount=%s, payment_method=%s, bank_account=%s,
                    cnic_attachment=%s, resume_attachment=%s, contract_attachment=%s, remarks=%s
                WHERE employee_id=%s
            """, (
                self.v_full_name.get(), self.v_role.get(), self.v_contact.get(), self.v_cnic.get(), self.v_address.get(),
                self.v_join_date.get(), self.v_contract.get(), self.v_shift.get(), self.v_status.get(),
                self.v_salary_type.get(), to_float(self.v_salary_amount.get()), self.v_payment_method.get(), self.v_bank_account.get(),
                self.v_cnic_path.get(), self.v_resume_path.get(), self.v_contract_path.get(), self.v_remarks.get(),
                self.employee_id
            ))
            con.commit(); con.close()
            messagebox.showinfo("Updated", "Employee updated.")
            self.load_table()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def delete_employee(self):
        if not self.employee_id:
            messagebox.showwarning("Select", "Select an employee from table.")
            return
        if messagebox.askyesno("Confirm", "Delete this employee? This will also delete their advances."):
            try:
                con = connect_db(); cur = con.cursor()
                cur.execute("DELETE FROM employees WHERE employee_id=%s", (self.employee_id,))
                con.commit(); con.close()
                messagebox.showinfo("Deleted", "Employee deleted.")
                self.clear_form()
                self.load_table()
            except Exception as e:
                messagebox.showerror("DB Error", str(e))

    def clear_form(self):
        self.employee_id = None
        self.v_full_name.set(""); self.v_role.set("")
        self.v_contact.set(""); self.v_cnic.set(""); self.v_address.set("")
        self.v_join_date.set(date.today().strftime("%Y-%m-%d"))
        self.v_contract.set("Permanent"); self.v_shift.set("Full Day"); self.v_status.set("Active")
        self.v_salary_type.set("Monthly"); self.v_salary_amount.set("0")
        self.v_payment_method.set("Cash"); self.v_bank_account.set("")
        self.v_cnic_path.set(""); self.v_resume_path.set(""); self.v_contract_path.set("")
        self.v_remarks.set("")

    # ------------------- TABLE LOAD & FILTER -------------------
    def apply_filters(self):
        self.load_table()

    def reset_filters(self):
        self.s_search.set("")
        self.f_role.set("All")
        self.f_status.set("All")
        self.load_table()

    def get_adv_outstanding(self, emp_id: int) -> float:
        con = connect_db(); cur = con.cursor()
        cur.execute("""
            SELECT 
                IFNULL(SUM(amount),0) AS total_adv,
                IFNULL(SUM(recovered_amount),0) AS total_rec
            FROM employee_advances WHERE employee_id=%s
        """, (emp_id,))
        row = cur.fetchone()
        con.close()
        if not row: return 0.0
        return float(row[0]) - float(row[1])

    def load_table(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = """
        SELECT employee_id, full_name, role, contact_number, cnic, join_date, contract_type,
               shift, status, salary_type, salary_amount, payment_method, bank_account
        FROM employees
        WHERE 1=1
        """
        args = []
        if self.f_role.get() != "All":
            q += " AND role=%s"
            args.append(self.f_role.get())
        if self.f_status.get() != "All":
            q += " AND status=%s"
            args.append(self.f_status.get())
        if self.s_search.get().strip():
            term = f"%{self.s_search.get().strip()}%"
            q += " AND (full_name LIKE %s OR role LIKE %s OR contact_number LIKE %s OR cnic LIKE %s)"
            args += [term, term, term, term]

        q += " ORDER BY employee_id DESC"

        con = connect_db(); cur = con.cursor()
        cur.execute(q, tuple(args))
        rows = cur.fetchall()
        con.close()

        # Summary counts
        total = len(rows)
        active = sum(1 for r in rows if r[8] == "Active")
        leave = sum(1 for r in rows if r[8] == "On Leave")
        resigned = sum(1 for r in rows if r[8] == "Resigned")
        self.summary_lbl.config(text=f"Employees: {total} | Active: {active} | On Leave: {leave} | Resigned: {resigned}")

        # Insert rows
        for row in rows:
            emp_id = row[0]
            adv_os = self.get_adv_outstanding(emp_id)
            self.tree.insert("", END, values=tuple(row) + (f"{adv_os:.2f}",))

    def fill_from_table(self, event):
        sel = self.tree.focus()
        if not sel: return
        data = self.tree.item(sel, "values")
        if not data: return
        self.employee_id = int(data[0])
        # load full row to populate all fields
        con = connect_db(); cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM employees WHERE employee_id=%s", (self.employee_id,))
        r = cur.fetchone()
        con.close()
        if not r: return
        self.v_full_name.set(r["full_name"])
        self.v_role.set(r["role"])
        self.v_contact.set(r["contact_number"] or "")
        self.v_cnic.set(r["cnic"] or "")
        self.v_address.set(r["address"] or "")
        self.v_join_date.set((r["join_date"] or date.today()).strftime("%Y-%m-%d") if isinstance(r["join_date"], (date, datetime)) else (r["join_date"] or ""))
        self.v_contract.set(r["contract_type"])
        self.v_shift.set(r["shift"])
        self.v_status.set(r["status"])
        self.v_salary_type.set(r["salary_type"])
        self.v_salary_amount.set(str(r["salary_amount"] or "0"))
        self.v_payment_method.set(r["payment_method"])
        self.v_bank_account.set(r["bank_account"] or "")
        self.v_cnic_path.set(r["cnic_attachment"] or "")
        self.v_resume_path.set(r["resume_attachment"] or "")
        self.v_contract_path.set(r["contract_attachment"] or "")
        self.v_remarks.set(r["remarks"] or "")

    # ------------------- EXPORT -------------------
    def export_csv(self):
        fpath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile="employees_export.csv")
        if not fpath: return
        try:
            con = connect_db(); cur = con.cursor()
            cur.execute("""
                SELECT employee_id, full_name, role, contact_number, cnic, join_date, contract_type,
                       shift, status, salary_type, salary_amount, payment_method, bank_account
                FROM employees ORDER BY employee_id DESC
            """)
            rows = cur.fetchall()
            con.close()
            headers = ["ID","Name","Role","Contact","CNIC","Join Date","Contract","Shift","Status","Salary Type","Salary","Payment Method","Bank/Wallet","Advance Outstanding"]
            with open(fpath, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(headers)
                for r in rows:
                    adv_os = self.get_adv_outstanding(r[0])
                    w.writerow(list(r) + [f"{adv_os:.2f}"])
            messagebox.showinfo("Exported", f"CSV saved:\n{fpath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ------------------- ADVANCE SALARY MODAL -------------------
    def open_advances(self):
        if not self.employee_id:
            messagebox.showwarning("Select", "Please select an employee first.")
            return
        AdvanceModal(self.root, self.employee_id, self.v_full_name.get(), self)


class AdvanceModal(Toplevel):
    def __init__(self, master, employee_id, emp_name, parent_form: EmployeesAdvancedForm):
        super().__init__(master)
        self.title(f"🧾 Advances — {emp_name} (ID: {employee_id})")
        self.geometry("850x520")
        self.employee_id = employee_id
        self.parent = parent_form
        self.configure(bg="white")

        # vars
        self.v_date = StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.v_amount = StringVar()
        self.v_recovered = StringVar(value="0")
        self.v_purpose = StringVar()
        self.v_notes = StringVar()

        # header
        Label(self, text=f"Advance Salary / Loan — {emp_name}", font=("Segoe UI", 14, "bold"),
              bg="#F59E0B", fg="white", pady=8).pack(fill=X)

        body = Frame(self, bg="white"); body.pack(fill=BOTH, expand=True, padx=10, pady=8)

        form = LabelFrame(body, text="New Entry", bg="white")
        form.pack(fill=X, padx=5, pady=(0,8))

        Label(form, text="Date", bg="white").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.datep = DateEntry(form, textvariable=self.v_date, width=14, date_pattern="yyyy-mm-dd")
        self.datep.grid(row=0, column=1, padx=4, pady=4)

        Label(form, text="Advance Amount *", bg="white").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        Entry(form, textvariable=self.v_amount, width=16).grid(row=0, column=3, padx=4, pady=4)

        Label(form, text="Recovered Now", bg="white").grid(row=0, column=4, sticky="w", padx=4, pady=4)
        Entry(form, textvariable=self.v_recovered, width=12).grid(row=0, column=5, padx=4, pady=4)

        Label(form, text="Purpose", bg="white").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        Entry(form, textvariable=self.v_purpose, width=36).grid(row=1, column=1, columnspan=3, padx=4, pady=4, sticky="w")

        Label(form, text="Notes", bg="white").grid(row=1, column=4, sticky="w", padx=4, pady=4)
        Entry(form, textvariable=self.v_notes, width=28).grid(row=1, column=5, padx=4, pady=4, sticky="w")

        Button(form, text="➕ Add Entry", bg="#1E3A8A", fg="white", command=self.add_advance).grid(row=2, column=5, sticky="e", padx=4, pady=6)

        # table
        table_frame = Frame(body, bg="white")
        table_frame.pack(fill=BOTH, expand=True)

        cols = ("id","advance_date","amount","recovered_amount","balance","purpose","notes")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        self.tree.pack(side=LEFT, fill=BOTH, expand=True, padx=(0,5))
        heads = ["ID","Date","Advance","Recovered","Balance","Purpose","Notes"]
        for c,h in zip(cols,heads):
            self.tree.heading(c, text=h)
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("advance_date", width=90, anchor="center")
        self.tree.column("amount", width=90, anchor="e")
        self.tree.column("recovered_amount", width=90, anchor="e")
        self.tree.column("balance", width=90, anchor="e")
        self.tree.column("purpose", width=160)
        self.tree.column("notes", width=200)

        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        # footer summary
        self.sum_lbl = Label(self, text="Total Advance: 0.00 | Recovered: 0.00 | Outstanding: 0.00",
                             bg="white", fg="#444")
        self.sum_lbl.pack(fill=X, padx=10, pady=(0,8))

        # action buttons
        actions = Frame(self, bg="white"); actions.pack(fill=X, padx=10, pady=(0,10))
        Button(actions, text="✏ Update Recovery", command=self.update_recovery).pack(side=LEFT)
        Button(actions, text="🗑 Delete Entry", command=self.delete_entry).pack(side=LEFT, padx=6)
        Button(actions, text="⬇ Export CSV", command=self.export_advances).pack(side=RIGHT)

        self.load_advances()

    # --- Advances CRUD ---
    def add_advance(self):
        amt = to_float(self.v_amount.get())
        rec = to_float(self.v_recovered.get())
        if amt <= 0:
            messagebox.showerror("Invalid", "Advance amount must be > 0.")
            return
        if rec < 0 or rec > amt:
            messagebox.showerror("Invalid", "Recovered cannot be negative or exceed advance.")
            return
        try:
            con = connect_db(); cur = con.cursor()
            cur.execute("""
                INSERT INTO employee_advances (employee_id, advance_date, amount, recovered_amount, purpose, notes)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (self.employee_id, self.v_date.get(), amt, rec, self.v_purpose.get(), self.v_notes.get()))
            con.commit(); con.close()
            self.load_advances()
            self.parent.load_table()
            self.v_amount.set(""); self.v_recovered.set("0"); self.v_purpose.set(""); self.v_notes.set("")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def load_advances(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        con = connect_db(); cur = con.cursor()
        cur.execute("""
            SELECT id, advance_date, amount, recovered_amount, purpose, notes
            FROM employee_advances
            WHERE employee_id=%s
            ORDER BY id DESC
        """, (self.employee_id,))
        rows = cur.fetchall()
        con.close()

        total = 0.0; recovered = 0.0
        for r in rows:
            bal = float(r[2]) - float(r[3])
            total += float(r[2]); recovered += float(r[3])
            self.tree.insert("", END, values=(r[0], r[1], f"{r[2]:.2f}", f"{r[3]:.2f}", f"{bal:.2f}", r[4], r[5]))
        outstanding = total - recovered
        self.sum_lbl.config(text=f"Total Advance: {total:.2f} | Recovered: {recovered:.2f} | Outstanding: {outstanding:.2f}")

    def get_selected_entry_id(self):
        sel = self.tree.focus()
        if not sel: return None
        vals = self.tree.item(sel,"values")
        if not vals: return None
        return int(vals[0])

    def update_recovery(self):
        eid = self.get_selected_entry_id()
        if not eid:
            messagebox.showwarning("Select", "Select an advance entry from table.")
            return
        # prompt for new recovery value
        top = Toplevel(self); top.title("Update Recovery"); top.geometry("300x150"); top.grab_set()
        v = StringVar(value="0")
        Label(top, text="Recovered Amount (+):").pack(pady=10)
        Entry(top, textvariable=v).pack()
        def do_update():
            add_rec = to_float(v.get())
            if add_rec < 0:
                messagebox.showerror("Invalid","Recovered cannot be negative."); return
            try:
                con = connect_db(); cur = con.cursor()
                # fetch current
                cur.execute("SELECT amount, recovered_amount FROM employee_advances WHERE id=%s", (eid,))
                r = cur.fetchone()
                if not r:
                    con.close(); top.destroy(); return
                amount, recovered = float(r[0]), float(r[1])
                new_rec = recovered + add_rec
                if new_rec > amount:
                    con.close()
                    messagebox.showerror("Invalid","Total recovered cannot exceed advance.")
                    return
                cur.execute("UPDATE employee_advances SET recovered_amount=%s WHERE id=%s", (new_rec, eid))
                con.commit(); con.close()
                top.destroy()
                self.load_advances()
                self.parent.load_table()
            except Exception as e:
                messagebox.showerror("DB Error", str(e))
        Button(top, text="Save", command=do_update).pack(pady=8)

    def delete_entry(self):
        eid = self.get_selected_entry_id()
        if not eid:
            messagebox.showwarning("Select", "Select an advance entry.")
            return
        if not messagebox.askyesno("Confirm","Delete this entry?"): return
        try:
            con = connect_db(); cur = con.cursor()
            cur.execute("DELETE FROM employee_advances WHERE id=%s", (eid,))
            con.commit(); con.close()
            self.load_advances()
            self.parent.load_table()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def export_advances(self):
        fpath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], initialfile=f"employee_{self.employee_id}_advances.csv")
        if not fpath: return
        try:
            con = connect_db(); cur = con.cursor()
            cur.execute("""
                SELECT id, advance_date, amount, recovered_amount, (amount-recovered_amount) AS balance, purpose, notes
                FROM employee_advances WHERE employee_id=%s ORDER BY id
            """, (self.employee_id,))
            rows = cur.fetchall(); con.close()
            with open(fpath,"w",newline="",encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["ID","Date","Advance","Recovered","Balance","Purpose","Notes"])
                w.writerows(rows)
            messagebox.showinfo("Exported", f"Saved:\n{fpath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))


# ---- Standalone run ----
if __name__ == "__main__":
    from tkinter import Tk
    ensure_tables()
    r = Tk()
    app = EmployeesAdvancedForm(r)
    r.mainloop()
