import streamlit as st
import sqlite3

# Replace with your actual database name
DATABASE_NAME = "reminders.db"

# Ensure the table exists
def create_table():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            text TEXT,
            modified_text TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_reminder(reminder):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO reminders (name, text, modified_text)
            VALUES (?, ?, ?)
        """, (reminder["Name"], reminder["Text"], reminder["Modified_Text"]))
        conn.commit()
        st.success("Reminder inserted!")
    except Exception as e:
        st.error(f"Failed to insert reminder: {e}")
    finally:
        conn.close()

def get_all_reminders():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reminders")
    data = cursor.fetchall()
    conn.close()
    return data

def delete_reminder(reminder_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()

# ------------------ Streamlit UI ------------------

st.title("📝 Reminder Manager")

# Create the table if it doesn't exist
create_table()

# Form to add a new reminder
st.subheader("Add a New Reminder")
with st.form("reminder_form"):
    name = st.text_input("Name")
    text = st.text_input("Text")
    modified_text = st.text_input("Modified Text")
    submitted = st.form_submit_button("Add Reminder")
    if submitted:
        new_reminder = {"Name": name, "Text": text, "Modified_Text": modified_text}
        insert_reminder(new_reminder)

# Display current reminders
st.subheader("Current Reminders")
reminders = get_all_reminders()

if reminders:
    for reminder in reminders:
        st.write(f"**ID**: {reminder[0]} | **Name**: {reminder[1]} | **Text**: {reminder[2]} | **Modified**: {reminder[3]}")
        if st.button(f"Delete ID {reminder[0]}", key=reminder[0]):
            delete_reminder(reminder[0])
            st.experimental_rerun()
else:
    st.info("No reminders found.")
