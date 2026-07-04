# -*- coding: utf-8 -*-
# Save as: main.py

import sys
import os
import tkinter as tk
import customtkinter as ctk

# Pure project root environment ki directory configuration system path me link karna
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Safe loading of Executive Dashboard Main Routing Frame
try:
    from forms.dashboard import MarqueeDashboard
except ModuleNotFoundError:
    try:
        from forms.dashboard import MarqueeDashboard
    except ImportError as e:
        print(f"[System Error] Enterprise Dashboard file could not be imported: {e}")
        sys.exit(1)

def initialize_marquee_system():
    """
    Main Boot Routine for Marquee Operations Management System.
    Overrides standard Tkinter initialization with CustomTkinter engine
    to enforce native dark styling rules globally across all child widgets.
    """
    # 1. PREMIUM THEMING PIPELINE SETUP
    # Setting up the Dark Catppuccin Mocha aesthetic base engine
    ctk.set_appearance_mode("Dark")             # Enforces systematic dark theme layout
    ctk.set_default_color_theme("blue")         # Custom modern accent curves mapping
    
    # 2. RUNTIME GRAPHICAL CONTAINER CONTEXT
    # Crucial Fix: Using ctk.CTk() instead of legacy tk.Tk() to stop UI and layout crashes!
    root = ctk.CTk()
    
    # Structural window mapping controls
    root.title("Marquee Management Operating System")
    root.geometry("1300x750")                   # Fixed screen grid geometry setup
    root.minsize(1100, 680)                     # Protect layout boundaries from getting small
    
    # Explicitly configure root frame canvas overlay matching Dashboard colors
    root.configure(fg_color="#1e1e2e")
    
    print("[Core Boot] CustomTkinter graphical window initiated smoothly. Injecting Dashboard Core...")

    # 3. EXECUTIVE SCREEN INJECTION MATRIX
    try:
        # Binding Dashboard frame pipeline directly onto top level active window
        app_dashboard = MarqueeDashboard(root)
        
        # Ensure layout alignment is synchronized across execution channels
        if hasattr(app_dashboard, "pack"):
            app_dashboard.pack(fill="both", expand=True)
            
    except Exception as runtime_init_exception:
        print(f"[Fatal Launch Exception] Dashboard frame assignment crash: {runtime_init_exception}")
        # Standard native window alert box backup if main loop window drops
        from tkinter import messagebox
        messagebox.showerror(
            "Application Engine Failure", 
            f"An error occurred while loading the Application Core Viewport:\n{str(runtime_init_exception)}"
        )
        sys.exit(1)

    # 4. START GLOBAL APPLICATION INTERACTIVE PIPELINE
    # Running infinite execution sequence loop to keep window awake and catch background tasks
    root.mainloop()

if __name__ == "__main__":
    # Launch system process cleanly
    initialize_marquee_system()