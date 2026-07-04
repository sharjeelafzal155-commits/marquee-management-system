# Marquee Management System 🏛️

A comprehensive desktop application built using Python and SQL to streamline marquee and banquet hall management. This software automates booking processes, financial tracking, and event scheduling to prevent conflicts and improve operational efficiency.

## ✨ Features
* **Event & Booking Management:** Schedule bookings with automated date checks to prevent double-booking (`booking_date` vs `event_date`).
* **Financial Tracking:** Maintain records of total sales, advances paid, remaining balances, and daily expenses.
* **Client Database:** Store customer contact details linked directly to their specific event records.
* **Profits & Reports:** Generate instant summaries of revenue and profits for the venue owners.

## 🛠️ Tech Stack
* **Language:** Python
* **Database:** SQLite (SQL)
* **GUI Framework:** Tkinter / CustomTkinter *(Note: Adjust this if you used another UI library)*

## 🚀 How It Works
1. **Launch the App:** Run the main application script (`main.py`).
2. **Book a Venue:** Enter client details, select the event date, package choice, and advance payment.
3. **Manage Expenses:** Log operational costs (catering, staff, electricity) to calculate net profits.
4. **Database Storage:** All records are instantly saved and managed inside the secure local database file.

## 📁 Project Structure
* `main.py` - The entry point of the application and main dashboard.
* `database.db` - SQLite database containing tables for bookings, clients, and expenses.
* *(Add other file names here if you want, e.g., billing.py, login.py)*

---
*Developed by Sharjeel Afzal*
