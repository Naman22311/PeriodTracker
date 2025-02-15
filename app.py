import streamlit as st
import sqlite3
import pandas as pd
import datetime
import calendar

# Database setup
conn = sqlite3.connect("period_tracker.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS periods (id INTEGER PRIMARY KEY, start_date TEXT, end_date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS symptoms (id INTEGER PRIMARY KEY, date TEXT, mood TEXT, cramps TEXT, flow TEXT)''')
conn.commit()

# Function to add period date
def add_period_date(start_date, end_date):
    c.execute("INSERT INTO periods (start_date, end_date) VALUES (?, ?)", (start_date, end_date))
    conn.commit()

# Function to update period date
def update_period_date(record_id, start_date, end_date):
    c.execute("UPDATE periods SET start_date = ?, end_date = ? WHERE id = ?", (start_date, end_date, record_id))
    conn.commit()

# Function to fetch period dates
def get_period_dates():
    c.execute("SELECT id, start_date, end_date FROM periods")
    return c.fetchall()

# Function to add symptoms
def add_symptoms(date, mood, cramps, flow):
    c.execute("INSERT INTO symptoms (date, mood, cramps, flow) VALUES (?, ?, ?, ?)", (date, mood, cramps, flow))
    conn.commit()

# UI Layout
st.title("Period Tracker")
st.sidebar.header("Log Your Period")

# Calendar to select period start and end dates
start_date = st.sidebar.date_input("Select period start date", datetime.date.today()).strftime("%d/%m/%y")
end_date = st.sidebar.date_input("Select period end date", datetime.date.today()).strftime("%d/%m/%y")
if st.sidebar.button("Add Period Date"):
    add_period_date(str(start_date), str(end_date))
    st.sidebar.success("Period dates added!")

# Modify existing period records
st.sidebar.header("Modify Period Entry")
period_records = get_period_dates()
if period_records:
    record_options = {f"ID {rec[0]}: {rec[1]} - {rec[2]}": rec[0] for rec in period_records}
    selected_record = st.sidebar.selectbox("Select a record to modify", list(record_options.keys()))
    selected_id = record_options[selected_record]
    new_start_date = st.sidebar.date_input("New Start Date", datetime.date.today()).strftime("%d/%m/%y")
    new_end_date = st.sidebar.date_input("New End Date", datetime.date.today()).strftime("%d/%m/%y")
    if st.sidebar.button("Update Period Date"):
        update_period_date(selected_id, new_start_date, new_end_date)
        st.sidebar.success("Period entry updated!")

# Calendar view of periods
st.subheader("Your Period Calendar")
period_dates = [(rec[1], rec[2]) for rec in period_records]
df_calendar = pd.DataFrame(period_dates, columns=["Start Date", "End Date"])
df_calendar["Start Date"] = pd.to_datetime(df_calendar["Start Date"], format="%d/%m/%y").dt.strftime("%d/%m/%y")
df_calendar["End Date"] = pd.to_datetime(df_calendar["End Date"], format="%d/%m/%y").dt.strftime("%d/%m/%y")
st.dataframe(df_calendar, height=400, width=800)



# Prediction Logic
if period_records:
    period_dates = sorted([datetime.datetime.strptime(date[0], "%d/%m/%y") for date in period_dates])
    cycle_lengths = [(period_dates[i] - period_dates[i-1]).days for i in range(1, len(period_dates))]
    if cycle_lengths:
        avg_cycle_length = sum(cycle_lengths) // len(cycle_lengths)
        next_period = period_dates[-1] + datetime.timedelta(days=avg_cycle_length)
        st.subheader("Predicted Next Period:")
        st.write(next_period.strftime("%d/%m/%y"))
    else:
        st.write("Not enough data to predict yet.")
else:
    st.write("No period data recorded yet.")

st.success("Your data is stored securely in a local database.")