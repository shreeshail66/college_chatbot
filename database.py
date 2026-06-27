"""
database.py
------------
Creates the SQLite database (college.db) and all required tables.
Also inserts some sample/demo data so the project works immediately
after setup, without you having to type everything in by hand.

Run this file ONCE before starting the app:
    python database.py
"""

import sqlite3

DB_NAME = "college.db"


def get_connection():
    """Helper used by app.py as well - returns a connection to the DB."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row   # lets us access columns by name
    return conn


def create_tables(conn):
    cur = conn.cursor()

    # 1. Students (login)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            department TEXT,
            year TEXT
        )
    """)

    # 2. Admin login
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # 3. Faculty information
    cur.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT,
            subject TEXT,
            email TEXT,
            cabin TEXT
        )
    """)

    # 4. Timetable
    cur.execute("""
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT,
            year TEXT,
            day TEXT,
            period TEXT,
            time_slot TEXT,
            subject TEXT,
            faculty_name TEXT
        )
    """)

    # 5. Attendance
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT,
            subject TEXT,
            total_classes INTEGER,
            attended_classes INTEGER
        )
    """)

    # 6. Knowledge base -> used for FAQs + chatbot answers + admin updates
    cur.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,         -- e.g. 'faq', 'general', 'fees', 'admission'
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    """)

    conn.commit()


def seed_data(conn):
    cur = conn.cursor()

    # ---- Demo student (roll_no: 101, password: 1234) ----
    cur.execute("SELECT COUNT(*) FROM students")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO students (roll_no, name, password, department, year) VALUES (?,?,?,?,?)",
            [
                ("101", "Rahul Sharma", "1234", "CSE", "3rd Year"),
                ("102", "Priya Singh", "1234", "CSE", "3rd Year"),
            ]
        )

    # ---- Demo admin (username: admin, password: admin123) ----
    cur.execute("SELECT COUNT(*) FROM admins")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO admins (username, password) VALUES (?,?)",
            ("admin", "admin123")
        )

    # ---- Faculty ----
    cur.execute("SELECT COUNT(*) FROM faculty")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO faculty (name, department, subject, email, cabin) VALUES (?,?,?,?,?)",
            [
                ("Dr. A. Kumar", "CSE", "Data Structures", "akumar@college.edu", "Room 201"),
                ("Prof. S. Mehta", "CSE", "Database Systems", "smehta@college.edu", "Room 204"),
                ("Dr. R. Iyer", "CSE", "Operating Systems", "riyer@college.edu", "Room 210"),
            ]
        )

    # ---- Timetable ----
    cur.execute("SELECT COUNT(*) FROM timetable")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO timetable (department, year, day, period, time_slot, subject, faculty_name) VALUES (?,?,?,?,?,?,?)",
            [
                ("CSE", "3rd Year", "Monday", "1", "9:00-10:00", "Data Structures", "Dr. A. Kumar"),
                ("CSE", "3rd Year", "Monday", "2", "10:00-11:00", "Database Systems", "Prof. S. Mehta"),
                ("CSE", "3rd Year", "Tuesday", "1", "9:00-10:00", "Operating Systems", "Dr. R. Iyer"),
                ("CSE", "3rd Year", "Tuesday", "2", "10:00-11:00", "Data Structures", "Dr. A. Kumar"),
            ]
        )

    # ---- Attendance ----
    cur.execute("SELECT COUNT(*) FROM attendance")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO attendance (roll_no, subject, total_classes, attended_classes) VALUES (?,?,?,?)",
            [
                ("101", "Data Structures", 40, 36),
                ("101", "Database Systems", 38, 30),
                ("101", "Operating Systems", 35, 33),
                ("102", "Data Structures", 40, 38),
                ("102", "Database Systems", 38, 34),
                ("102", "Operating Systems", 35, 20),
            ]
        )

    # ---- Knowledge base / FAQs (this is what the chatbot searches) ----
    cur.execute("SELECT COUNT(*) FROM knowledge_base")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO knowledge_base (category, question, answer) VALUES (?,?,?)",
            [
                ("faq", "What are the college timings?",
                 "The college works from 9:00 AM to 4:00 PM, Monday to Saturday."),
                ("faq", "How can I apply for a leave of absence?",
                 "Submit a leave application to your class coordinator with a valid reason, "
                 "at least one day in advance."),
                ("faq", "Where is the college library located?",
                 "The library is on the ground floor of the main academic block, "
                 "open from 9 AM to 6 PM."),
                ("faq", "What is the minimum attendance required?",
                 "Students must maintain at least 75% attendance in every subject "
                 "to be eligible for end-semester exams."),
                ("admission", "How do I get admission to the CSE department?",
                 "Admissions are based on entrance exam rank and counselling. "
                 "Visit the admission office or college website for the application form."),
                ("fees", "How can I pay my college fees?",
                 "Fees can be paid online through the college portal, or offline at the "
                 "accounts office, before the due date each semester."),
                ("general", "Who is the head of the CSE department?",
                 "Dr. A. Kumar is the current Head of the Computer Science department."),
                ("general", "How do I contact the college?",
                 "You can email info@college.edu or call the front office at +91-XXXXXXXXXX."),
            ]
        )

    conn.commit()


if __name__ == "__main__":
    conn = get_connection()
    create_tables(conn)
    seed_data(conn)
    conn.close()
    print("✅ Database 'college.db' created and seeded with sample data.")
