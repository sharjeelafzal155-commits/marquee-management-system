# -*- coding: utf-8 -*-
# Save as: forms/dashboard.py

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
from datetime import date
import subprocess
import sys
import os

# Professional graphs engines 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Database Framework connector dependency
from db.connection import connect_database

# Modern Enterprise Catppuccin Mocha-Inspired Dark Palette 
THEME_BG = "#1e1e2e"       # Dark Charcoal Base
SIDEBAR_BG = "#181825"    # Deep Slate Sidebar
CARD_BG = "#313244"       # Card Background
ACCENT_COLOR = "#cba6f7"  # Electric Purple Brand
TEXT_PRIMARY = "#cdd6f4"  # Off-White Text
TEXT_MUTED = "#a6adc8"    # Gray Text

# Safe Module Routing Matrix - Dynamic absolute fallbacks to completely bypass ModuleNotFoundError
try:
    from forms.booking_form import BookingForm
except ModuleNotFoundError:
    try:
        from booking_form import BookingForm
    except ImportError:
        BookingForm = None

try:
    from forms.expense_form import ExpenseForm
except ModuleNotFoundError:
    try:
        from expense_form import ExpenseForm
    except ImportError:
        ExpenseForm = None

try:
    from forms.khaata_chicken_form import KhaataChickenPoultryForm
except ModuleNotFoundError:
    try:
        from khaata_chicken_form import KhaataChickenPoultryForm
    except ImportError:
        KhaataChickenPoultryForm = None

try:
    from forms.khaata_meat_form import KhaataMeatForm
except ModuleNotFoundError:
    try:
        from khaata_meat_form import KhaataMeatForm
    except ImportError:
        KhaataMeatForm = None

try:
    from forms.khaata_milk_dairy_form import KhaataMilkDairyForm
except ModuleNotFoundError:
    try:
        from khaata_milk_dairy_form import KhaataMilkDairyForm
    except ImportError:
        KhaataMilkDairyForm = None

try:
    from forms.khaata_karyana_form import KhaataKaryanaForm
except ModuleNotFoundError:
    try:
        from khaata_karyana_form import KhaataKaryanaForm
    except ImportError:
        KhaataKaryanaForm = None

try:
    from forms.khaata_cold_drinks_form import KhaataColdDrinksForm
except ModuleNotFoundError:
    try:
        from khaata_cold_drinks_form import KhaataColdDrinksForm
    except ImportError:
        KhaataColdDrinksForm = None

try:
    from forms.khaata_fruits_vegs_form import KhaataFruitsVegsForm
except ModuleNotFoundError:
    try:
        from khaata_fruits_vegs_form import KhaataFruitsVegsForm
    except ImportError:
        KhaataFruitsVegsForm = None

try:
    from forms.employee_form import EmployeeForm
except ModuleNotFoundError:
    try:
        from employee_form import EmployeeForm
    except ImportError:
        EmployeeForm = None

try:
    from forms.temp_employees_form import TempEmployeesForm
except ModuleNotFoundError:
    try:
        from temp_employees_form import TempEmployeesForm
    except ImportError:
        TempEmployeesForm = None

try:
    from forms.reports import ReportsScreen
except ModuleNotFoundError:
    try:
        from reports import ReportsScreen
    except ImportError:
        ReportsScreen = None

try:
    from forms.owner_share_summary import OwnerShareSummaryScreen
except ModuleNotFoundError:
    try:
        from owner_share_summary import OwnerShareSummaryScreen
    except ImportError:
        OwnerShareSummaryScreen = None


class MarqueeDashboard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        # Initializing as a sub-frame component linked to master main window
        super().__init__(master, fg_color=THEME_BG, **kwargs)
        self.master = master
        self.pack(fill="both", expand=True)
        
        # Inject styling rules matrix directly to inner ttk objects
        self.configure_native_ttk_styles()
        
        # State tracking variable to avoid duplicate workspace allocation leaks
        self.active_submodule_view = None
        
        # Build layout structure
        self.setup_main_layout_matrix()
        
        # Initialize Core Business Intelligence Dashboard Metrics View
        self.route_home_dashboard()

    def configure_native_ttk_styles(self):
        """Maps out global ttk stylesheet layer overrides for clean visuals consistency."""
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Treeview", 
                        background=CARD_BG, 
                        fieldbackground=CARD_BG, 
                        foreground=TEXT_PRIMARY, 
                        rowheight=28, 
                        borderwidth=0, 
                        font=("Segoe UI", 10))
        
        style.configure("Treeview.Heading", 
                        background=SIDEBAR_BG, 
                        foreground=ACCENT_COLOR, 
                        relief="flat", 
                        font=("Segoe UI", 10, "bold"))
        
        style.map("Treeview", background=[("selected", ACCENT_COLOR)], foreground=[("selected", "#11111b")])
        style.map("Treeview.Heading", background=[("active", CARD_BG)], foreground=[("active", TEXT_PRIMARY)])

    def setup_main_layout_matrix(self):
        """Constructs the absolute layout foundation grid system channels wrappers."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- LEFT CONTROLS NAVIGATION SIDEBAR PANEL ---
        self.sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        lbl_branding = ctk.CTkLabel(self.sidebar, text="MARQUEE CORE", 
                                    font=ctk.CTkFont(family="Consolas", size=20, weight="bold"), 
                                    text_color=ACCENT_COLOR)
        lbl_branding.pack(pady=(25, 2), padx=15, anchor="w")
        
        lbl_sub_brand = ctk.CTkLabel(self.sidebar, text="Financial System v3.1", 
                                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        lbl_sub_brand.pack(pady=(0, 20), padx=15, anchor="w")
        
        # Navigation Actions Trigger Buttons (Using exact allowed 'normal' weight architecture)
        self.create_nav_button("Dashboard Overview", "🏠", self.route_home_dashboard)
        self.create_nav_button("Event Bookings", "📅", self.route_bookings)
        self.create_nav_button("Central Expenses Log", "💸", self.route_expenses)
        
        lbl_sep_khaata = ctk.CTkLabel(self.sidebar, text="INVENTORY & KHAATAS", 
                                      font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED)
        lbl_sep_khaata.pack(pady=(15, 5), padx=15, anchor="w")
        
        self.create_nav_button("Poultry (Chicken) Khaata", "🐓", self.route_khaata_chicken)
        self.create_nav_button("Meat (Mutton/Beef)", "🥩", self.route_khaata_meat)
        self.create_nav_button("Dairy & Milk Supply", "🥛", self.route_khaata_milk_dairy)
        self.create_nav_button("Karyana Inventory", "🛒", self.route_khaata_karyana)
        self.create_nav_button("Cold Drinks Stock", "🥤", self.route_khaata_cold_drinks)
        self.create_nav_button("Fruits & Vegetables", "🥦", self.route_khaata_fruits_vegs)
        
        lbl_sep_hr = ctk.CTkLabel(self.sidebar, text="HUMAN RESOURCES (HR)", 
                                  font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED)
        lbl_sep_hr.pack(pady=(15, 5), padx=15, anchor="w")
        
        self.create_nav_button("Permanent Staff Payroll", "👔", self.route_employees)
        self.create_nav_button("Temporary Event Staff", "🏃", self.route_temp_employees)
        
        lbl_sep_mgmt = ctk.CTkLabel(self.sidebar, text="ANALYTICS & EQUITY", 
                                    font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED)
        lbl_sep_mgmt.pack(pady=(15, 5), padx=15, anchor="w")
        
        self.create_nav_button("Financial Reports", "📈", self.route_reports)
        self.create_nav_button("Owners Share Distribution", "🤝", self.route_owner_shares)
        
        utility_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        utility_container.pack(side="bottom", fill="x", pady=15, padx=10)
        
        btn_backup = ctk.CTkButton(utility_container, text=" Database Backup", image=None,
                                    fg_color="#313244", hover_color="#45475a", text_color=TEXT_PRIMARY,
                                    font=ctk.CTkFont(size=12, weight="bold"), height=32,
                                    command=self.execute_system_backup)
        btn_backup.pack(fill="x")

        # --- RIGHT MAIN WORKSPACE HOST LAYER CANVAS ---
        self.workspace = ctk.CTkFrame(self, fg_color=THEME_BG, corner_radius=0)
        self.workspace.grid(row=0, column=1, sticky="nsew")

    def create_nav_button(self, label_text, emoji_icon, target_route_command):
        # Strict validation override: forced to exact system 'normal' font weights
        btn = ctk.CTkButton(self.sidebar, text=f" {emoji_icon}  {label_text}", 
                            anchor="w", fg_color="transparent", hover_color=CARD_BG, 
                            text_color=TEXT_PRIMARY, font=ctk.CTkFont(size=12, weight="normal"),
                            height=34, corner_radius=6, command=target_route_command)
        btn.pack(fill="x", padx=10, pady=2)
        return btn

    def _clear_workspace(self):
        try:
            plt.close('all')
        except Exception:
            pass
            
        if self.active_submodule_view is not None:
            try:
                self.active_submodule_view.destroy()
            except Exception:
                pass
        
        for dynamic_child in self.workspace.winfo_children():
            try:
                dynamic_child.destroy()
            except Exception:
                pass
                
        self.active_submodule_view = None

    def _show_missing_module_error(self, filename_marker):
        messagebox.showerror("Module Resolution Error", 
                             f"The required system sheet script '{filename_marker}' is currently unresolvable or contain deep errors inside.\n\nPlease place the accurate implementation module inside the targeted 'forms/' folder.")

    def route_home_dashboard(self):
        self._clear_workspace()
        
        scrollable_home_frame = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent")
        scrollable_home_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_panel = ctk.CTkFrame(scrollable_home_frame, fg_color="transparent")
        header_panel.pack(fill="x", pady=(0, 15))
        
        lbl_welcome = ctk.CTkLabel(header_panel, text="Marquee Live Operational Analytics Hub", 
                                   font=ctk.CTkFont(size=22, weight="bold"), text_color=TEXT_PRIMARY)
        lbl_welcome.pack(side="left", anchor="w")
        
        # FIXED: Changed weight from 'medium' to 'normal' to entirely prevent Windows crash
        lbl_date = ctk.CTkLabel(header_panel, text=f"System Date Node: {date.today().strftime('%A, %d %B %Y')}", 
                                font=ctk.CTkFont(size=12, weight="normal"), text_color=ACCENT_COLOR)
        lbl_date.pack(side="right", anchor="e", pady=8)
        
        kpi_grid_row = ctk.CTkFrame(scrollable_home_frame, fg_color="transparent")
        kpi_grid_row.pack(fill="x", pady=10)
        kpi_grid_row.columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi_equal")
        
        self.kpi_confirmed_bookings_count = tk.StringVar(value="0 Events")
        self.kpi_gross_revenue_pool = tk.StringVar(value="PKR 0.00")
        self.kpi_consolidated_expenses_pool = tk.StringVar(value="PKR 0.00")
        self.kpi_net_profit_delta_margin = tk.StringVar(value="PKR 0.00")
        
        self.render_kpi_card_node(kpi_grid_row, 0, "CONFIRMED EVENTS", self.kpi_confirmed_bookings_count, "#a6e3a1")
        self.render_kpi_card_node(kpi_grid_row, 1, "GROSS REVENUE STREAM", self.kpi_gross_revenue_pool, "#b4befe")
        self.render_kpi_card_node(kpi_grid_row, 2, "TOTAL OPERATIONAL OUTFLOW", self.kpi_consolidated_expenses_pool, "#f38ba8")
        self.render_kpi_card_node(kpi_grid_row, 3, "NET SURPLUS VALUE", self.kpi_net_profit_delta_margin, "#cba6f7")
        
        analytics_split_row = ctk.CTkFrame(scrollable_home_frame, fg_color="transparent")
        analytics_split_row.pack(fill="both", expand=True, pady=15)
        analytics_split_row.columnconfigure(0, weight=5, uniform="split_ratio")
        analytics_split_row.columnconfigure(1, weight=4, uniform="split_ratio")
        
        graph_card_wrapper = ctk.CTkFrame(analytics_split_row, fg_color=CARD_BG, corner_radius=12)
        graph_card_wrapper.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        lbl_graph_title = ctk.CTkLabel(graph_card_wrapper, text="Financial Breakdown Chart", 
                                       font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY)
        lbl_graph_title.pack(anchor="w", padx=15, pady=15)
        
        table_card_wrapper = ctk.CTkFrame(analytics_split_row, fg_color=CARD_BG, corner_radius=12)
        table_card_wrapper.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        lbl_table_title = ctk.CTkLabel(table_card_wrapper, text="Upcoming Events Schedule", 
                                       font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY)
        lbl_table_title.pack(anchor="w", padx=15, pady=15)
        
        self.tbl_upcoming_events = ttk.Treeview(table_card_wrapper, columns=("Client", "Date", "Hall"), show="headings")
        self.tbl_upcoming_events.heading("Client", text="Client Name")
        self.tbl_upcoming_events.heading("Date", text="Event Date")
        self.tbl_upcoming_events.heading("Hall", text="Hall Arena")
        
        self.tbl_upcoming_events.column("Client", width=120, anchor="w")
        self.tbl_upcoming_events.column("Date", width=90, anchor="center")
        self.tbl_upcoming_events.column("Hall", width=100, anchor="w")
        self.tbl_upcoming_events.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.load_kpi_metrics(graph_card_wrapper)

    def render_kpi_card_node(self, parent_row_frame, col_idx, structural_label_txt, reactive_str_ptr, border_hex):
        card_box = ctk.CTkFrame(parent_row_frame, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=border_hex)
        card_box.grid(row=0, column=col_idx, padx=6, pady=5, sticky="nsew")
        
        lbl_meta = ctk.CTkLabel(card_box, text=structural_label_txt, font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED)
        lbl_meta.pack(pady=(12, 2), padx=15, anchor="w")
        
        lbl_num = ctk.CTkLabel(card_box, textvariable=reactive_str_ptr, font=ctk.CTkFont(family="Consolas", size=18, weight="bold"), text_color=border_hex)
        lbl_num.pack(pady=(0, 12), padx=15, anchor="w")

    def load_kpi_metrics(self, visual_graph_parent_card_node):
        conn = connect_database()
        if not conn: return
            
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM bookings WHERE booking_status = 'Confirmed'")
            active_events_count = int(cur.fetchone()[0])
            self.kpi_confirmed_bookings_count.set(f"{active_events_count} Active Events")
            
            cur.execute("SELECT COALESCE(SUM(number_of_guests * per_person_charge), 0) FROM bookings WHERE booking_status != 'Cancelled'")
            gross_revenue_total_val = float(cur.fetchone()[0])
            self.kpi_gross_revenue_pool.set(f"PKR {gross_revenue_total_val:,.2f}")
            
            cur.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses")
            total_expenses_outflow_val = float(cur.fetchone()[0])
            self.kpi_consolidated_expenses_pool.set(f"PKR {total_expenses_outflow_val:,.2f}")
            
            net_profit_delta_margin_val = gross_revenue_total_val - total_expenses_outflow_val
            self.kpi_net_profit_delta_margin.set(f"PKR {net_profit_delta_margin_val:,.2f}")
            
            cur.execute("SELECT customer_name, event_date, hall_name FROM bookings WHERE event_date >= CURDATE() AND booking_status = 'Confirmed' ORDER BY event_date ASC LIMIT 8")
            upcoming_dataset_rows = cur.fetchall()
            
            for active_row in self.tbl_upcoming_events.get_children():
                self.tbl_upcoming_events.delete(active_row)
                
            for record in upcoming_dataset_rows:
                self.tbl_upcoming_events.insert("", "end", values=(record[0], str(record[1]), record[2]))
                
            conn.close()
            self.render_dashboard_charts_matrix(visual_graph_parent_card_node, gross_revenue_total_val, total_expenses_outflow_val, net_profit_delta_margin_val)
            
        except Exception as dynamic_query_fault:
            if conn: conn.close()
            print(f"[System Diagnostic Matrix Recovery Error]: {str(dynamic_query_fault)}")

    def render_dashboard_charts_matrix(self, host_wrapper_card_node, rev_val, exp_val, profit_val):
        plt.style.use('dark_background')
        fig, axis_node = plt.subplots(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor(CARD_BG)
        axis_node.set_facecolor(CARD_BG)
        
        target_labels_metrics_categories = ['Revenue', 'Expenses', 'Net Profit']
        financial_numerical_values = [rev_val, exp_val, max(0.0, profit_val)]
        structural_hex_bar_colors = ['#b4befe', '#f38ba8', '#cba6f7']
        
        axis_node.bar(target_labels_metrics_categories, financial_numerical_values, color=structural_hex_bar_colors, width=0.5)
        axis_node.tick_params(axis='x', colors=TEXT_PRIMARY, labelsize=9)
        axis_node.tick_params(axis='y', colors=TEXT_MUTED, labelsize=8)
        
        for edge_spine_key in ['top', 'right', 'left', 'bottom']:
            axis_node.spines[edge_spine_key].set_visible(False)
            
        axis_node.yaxis.grid(True, linestyle='--', alpha=0.1, color=TEXT_PRIMARY)
        fig.tight_layout()
        
        canvas_widget_mount_node = FigureCanvasTkAgg(fig, master=host_wrapper_card_node)
        canvas_widget_mount_node.draw()
        canvas_widget_mount_node.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))

    # --- SUBMODULE FORMS SUB-ROUTINGS ---
    def route_bookings(self): 
        if BookingForm is None:
            self._show_missing_module_error("booking_form.py")
            return
        self._clear_workspace()
        try:
            self.active_submodule_view = BookingForm(self.workspace)
        except Exception as e:
            self._show_missing_module_error(f"booking_form.py (Runtime Init Error: {str(e)})")

    def route_expenses(self): 
        if ExpenseForm is None:
            self._show_missing_module_error("expense_form.py")
            return
        self._clear_workspace()
        try:
            self.active_submodule_view = ExpenseForm(self.workspace)
            if hasattr(self.active_submodule_view, "pack"):
                self.active_submodule_view.pack(fill="both", expand=True)
        except Exception as e:
            self._show_missing_module_error(f"expense_form.py (Runtime Init Error: {str(e)})")

    def route_khaata_chicken(self): 
        if KhaataChickenPoultryForm is None:
            self._show_missing_module_error("khaata_chicken_form.py")
            return
        self._clear_workspace()
        try:
            self.active_submodule_view = KhaataChickenPoultryForm(self.workspace)
            if hasattr(self.active_submodule_view, "pack"):
                self.active_submodule_view.pack(fill="both", expand=True)
        except Exception as e:
            self._show_missing_module_error(f"khaata_chicken_form.py (Runtime Init Error: {str(e)})")

    def route_khaata_meat(self): 
        if KhaataMeatForm is None:
            self._show_missing_module_error("khaata_meat_form.py")
            return
        self._clear_workspace()
        try:
            self.active_submodule_view = KhaataMeatForm(self.workspace)
            if hasattr(self.active_submodule_view, "pack"):
                self.active_submodule_view.pack(fill="both", expand=True)
        except Exception as e:
            self._show_missing_module_error(f"khaata_meat_form.py (Runtime Init Error: {str(e)})")

    def route_khaata_milk_dairy(self): 
        if KhaataMilkDairyForm is None:
            self._show_missing_module_error("khaata_milk_dairy_form.py")
            return
        self._clear_workspace()
        try:
            self.active_submodule_view = KhaataMilkDairyForm(self.workspace)
            if hasattr(self.active_submodule_view, "pack"):
                self.active_submodule_view.pack(fill="both", expand=True)
        except Exception as e:
            self._show_missing_module_error(f"khaata_milk_dairy_form.py (Runtime Init Error: {str(e)})")

    def route_khaata_karyana(self): 
        if KhaataKaryanaForm is None:
            self._show_missing_module_error("khaata_karyana_form.py")
            return
        self._clear_workspace()
        try:
            self.active_submodule_view = KhaataKaryanaForm(self.workspace)
            if hasattr(self.active_submodule_view, "pack"):
                self.active_submodule_view.pack(fill="both", expand=True)
        except Exception as e:
            self._show_missing_module_error(f"khaata_karyana_form.py (Runtime Init Error: {str(e)})")

    def route_khaata_cold_drinks(self): 
        if KhaataColdDrinksForm is None:
            self._show_missing_module_error("khaata_cold_drinks_form.py")
            return
        self._clear_workspace()
        try:
            self.active_submodule_view = KhaataColdDrinksForm(self.workspace)
            if hasattr(self.active_submodule_view, "pack"):
                self.active_submodule_view.pack(fill="both", expand=True)
        except Exception as e:
            self._show_missing_module_error(f"khaata_cold_drinks_form.py (Runtime Init Error: {str(e)})")

    def route_khaata_fruits_vegs(self): 
        if KhaataFruitsVegsForm is None:
            self._show_missing_module_error("khaata_fruits_vegs_form.py")
            return
        self._clear_workspace()
        try:
            self.active_submodule_view = KhaataFruitsVegsForm(self.workspace)
            if hasattr(self.active_submodule_view, "pack"):
                self.active_submodule_view.pack(fill="both", expand=True)
        except Exception as e:
            self._show_missing_module_error(f"khaata_fruits_vegs_form.py (Runtime Init Error: {str(e)})")

    def route_employees(self): 
        if EmployeeForm is None:
            self._show_missing_module_error("employee_form.py")
            return
        self._clear_workspace()
        try:
            self.active_submodule_view = EmployeeForm(self.workspace)
            if hasattr(self.active_submodule_view, "pack"):
                self.active_submodule_view.pack(fill="both", expand=True)
        except Exception as e:
            self._show_missing_module_error(f"employee_form.py (Runtime Init Error: {str(e)})")

    def route_temp_employees(self): 
        if TempEmployeesForm is None:
            self._show_missing_module_error("temp_employees_form.py")
            return
        self._clear_workspace()
        try:
            self.active_submodule_view = TempEmployeesForm(self.workspace)
            if hasattr(self.active_submodule_view, "pack"):
                self.active_submodule_view.pack(fill="both", expand=True)
        except Exception as e:
            self._show_missing_module_error(f"temp_employees_form.py (Runtime Init Error: {str(e)})")

    def route_reports(self): 
        if ReportsScreen is None:
            self._show_missing_module_error("reports.py")
            return
        self._clear_workspace()
        try:
            self.active_submodule_view = ReportsScreen(self.workspace)
            if hasattr(self.active_submodule_view, "pack"):
                self.active_submodule_view.pack(fill="both", expand=True)
        except Exception as e:
            self._show_missing_module_error(f"reports.py (Runtime Init Error: {str(e)})")

    def route_owner_shares(self): 
        if OwnerShareSummaryScreen is None:
            self._show_missing_module_error("owner_share_summary.py")
            return
        self._clear_workspace()
        try:
            self.active_submodule_view = OwnerShareSummaryScreen(self.workspace)
            if hasattr(self.active_submodule_view, "pack"):
                self.active_submodule_view.pack(fill="both", expand=True)
        except Exception as e:
            self._show_missing_module_error(f"owner_share_summary.py (Runtime Init Error: {str(e)})")

    def execute_system_backup(self):
        try:
            today = date.today().strftime("%Y-%m-%d")
            file_path = filedialog.asksaveasfilename(
                defaultextension=".sql", initialfile=f"marquee_backup_{today}.sql",
                filetypes=[("SQL Backup files", "*.sql")]
            )
            if not file_path: return
                
            with open(file_path, "w", encoding="utf-8") as f:
                res = subprocess.run(["mysqldump", "-u", "root", "marquee_management"], stdout=f, stderr=subprocess.PIPE, text=True)
                
            if res.returncode == 0:
                messagebox.showinfo("Backup Vault", f"Database snapshotted successfully to:\n{file_path}")
            else:
                messagebox.showerror("Backup Interrupted", f"Core backup pipeline aborted. Error:\n{res.stderr}")
        except Exception as critical_io_fault:
            messagebox.showerror("IO Dump Error", str(critical_io_fault))


# Create an alias for main.py mapping compatibility
Dashboard = MarqueeDashboard

if __name__ == "__main__":
    # Fallback initialization window loop if executed standalone
    root = ctk.CTk()
    root.geometry("1280x720")
    app_instance = MarqueeDashboard(root)
    root.mainloop()