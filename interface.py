import streamlit as st
import sqlite3

DATABASE_NAME = "reminders.db"

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

st.set_page_config(page_title="Reminder Manager", layout="wide")
st.title("Reminder Manager")

create_table()

st.subheader("Add a New Reminder")
with st.form("reminder_form"):
    cols = st.columns(3)
    name = cols[0].text_input("Name")
    text = cols[1].text_input("Text")
    modified_text = cols[2].text_input("Modified Text")
    submitted = st.form_submit_button("Add Reminder")
    if submitted:
        new_reminder = {"Name": name, "Text": text, "Modified_Text": modified_text}
        insert_reminder(new_reminder)
        st.rerun()

st.subheader("Current Reminders")
reminders = get_all_reminders()

if reminders:
    for reminder in reminders:
        id_, name, text, modified_text = reminder
        cols = st.columns([4, 4, 4, 1])
        with cols[0]:
            st.markdown(f"**Name:** {name}", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"**Text:** {text}", unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"**Modified:** {modified_text}", unsafe_allow_html=True)
        with cols[3]:
            if st.button("Delete", key=f"delete_{id_}"):
                delete_reminder(id_)
                st.rerun()
else:
    st.info("No reminders found.")
