# Save as: db/connection.py
import mysql.connector
from tkinter import messagebox

def connect_database():
    """Centralized secure connection pool for the entire Marquee Core."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="marquee_management" # Apni DB database ka sahi naam yahan check kar lein
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Critical Error", f"SQL Connection Failed:\n{err}")
        return None

# Fallback alias taaky puranay aur naye sub-khaata forms crash na hon
def connect_db():
    return connect_database()