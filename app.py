import streamlit as st
import mysql.connector
from datetime import datetime
import pandas as pd

# Database connection configuration
def get_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="pesu_admin ",
        password="1234",
        database="pesu_clubs_event_management"
    )

# Initialize session state for user authentication
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
    st.session_state.user_role = None

# Login functionality
def login_user():
    st.title("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            query = "SELECT role FROM users WHERE email = %s AND password = %s"
            result = execute_query(query, (email, password), fetch=True)
            if result:
                st.session_state.user_email = email
                st.session_state.user_role = result[0]['role']
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

# Database operations
def execute_query(query, params=None, fetch=False):
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
        else:
            result = None
            conn.commit()
            
        return result
    except mysql.connector.Error as err:
        st.error(f"Database Error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

# Dashboard page
def show_dashboard():
    st.title('PESU Clubs Dashboard')
    
    # Display upcoming events
    st.subheader('Upcoming Events')
    events_query = """
    SELECT e.title, e.start_date, e.duration, e.number_of_participants, 
           e.location, e.budget, c.club_name
    FROM EVENT e
    JOIN CLUB c ON e.club_id = c.club_name
    WHERE e.start_date >= CURDATE()
    ORDER BY e.start_date
    """
    events = execute_query(events_query, fetch=True)
    if events:
        events_df = pd.DataFrame(events)
        st.dataframe(events_df)
    
    # Display club statistics
    st.subheader('Club Statistics')
    club_stats_query = """
    SELECT c.club_name, c.club_email, c.instagram_handle, 
           c.number_of_members, 
           COUNT(e.event_id) as total_events
    FROM CLUB c
    LEFT JOIN EVENT e ON c.club_name = e.club_id
    GROUP BY c.club_name, c.club_email, c.instagram_handle, c.number_of_members
    """
    club_stats = execute_query(club_stats_query, fetch=True)
    if club_stats:
        stats_df = pd.DataFrame(club_stats)
        st.dataframe(stats_df)

# Event Management page
def show_event_management():
    st.title('Event Management')
    
    # Add new event form
    st.subheader('Add New Event')
    with st.form('new_event_form'):
        # Get clubs for dropdown
        clubs = execute_query("SELECT club_name FROM CLUB", fetch=True)
        club_names = [club['club_name'] for club in clubs]
        
        title = st.text_input('Event Title')
        club_name = st.selectbox('Club', options=club_names)
        start_date = st.date_input('Event Date')
        duration = st.number_input('Duration (hours)', min_value=1)
        location = st.text_input('Location')
        budget = st.number_input('Budget', min_value=0.0, step=100.0)
        
        submit = st.form_submit_button('Create Event')
        
        if submit:
            if title and club_name and start_date and duration and location:
                query = """
                INSERT INTO EVENT (title, club_id, start_date, duration, location, budget)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                params = (title, club_name, start_date, duration, location, budget)
                execute_query(query, params)
                st.success('Event created successfully!')
            else:
                st.error('Please fill all required fields')
    
    # Display and manage existing events
    st.subheader('Existing Events')
    events = execute_query("""
        SELECT e.event_id, e.title, e.club_id, e.start_date, e.duration, 
               e.location, e.budget, e.number_of_participants
        FROM EVENT e
        ORDER BY e.start_date DESC
    """, fetch=True)
    
    if events:
        events_df = pd.DataFrame(events)
        st.dataframe(events_df)
        
        # Delete event section
        event_to_delete = st.selectbox('Select event to delete', 
                                     options=[event['title'] for event in events])
        if st.button('Delete Event'):
            event_id = next(event['event_id'] for event in events 
                          if event['title'] == event_to_delete)
            execute_query("DELETE FROM EVENT WHERE event_id = %s", (event_id,))
            st.success('Event deleted successfully!')
            st.rerun()

# Club Registration page
def show_club_registration():
    st.title('Club Member Registration')
    
    # New member registration form
    st.subheader('Register as Club Member')
    with st.form('registration_form'):
        member_srn = st.text_input('SRN')
        name = st.text_input('Name')
        email = st.text_input('Email')
        phone_number = st.text_input('Phone Number')
        cgpa = st.number_input('CGPA', min_value=0.0, max_value=10.0, step=0.01)
        
        # Get departments for dropdown
        departments = execute_query("SELECT depart_id, department_name FROM DEPARTMENT", fetch=True)
        dept_dict = {dept['department_name']: dept['depart_id'] for dept in departments}
        department = st.selectbox('Department', options=list(dept_dict.keys()))
        
        submit = st.form_submit_button('Register')
        
        if submit:
            if member_srn and name and email and phone_number and department:
                # Check if member already exists
                existing_member = execute_query(
                    "SELECT * FROM CLUB_MEMBER WHERE member_srn = %s",
                    (member_srn,),
                    fetch=True
                )
                
                if not existing_member:
                    query = """
                    INSERT INTO CLUB_MEMBER (member_srn, name, email, phone_number, cgpa, depart_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    params = (member_srn, name, email, phone_number, cgpa, dept_dict[department])
                    execute_query(query, params)
                    st.success('Registration successful!')
                else:
                    st.error('Member already exists')
            else:
                st.error('Please fill all required fields')

# Main app logic
if not st.session_state.user_email:
    login_user()
else:
    st.sidebar.title('PESU Clubs')
    st.sidebar.text(f'Logged in as: {st.session_state.user_email}')
    st.sidebar.text(f'Role: {st.session_state.user_role}')
    
    if st.sidebar.button('Logout'):
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.rerun()
    
    page = st.sidebar.radio('Navigation', ['Dashboard', 'Event Management', 'Club Registration'])
    
    if page == 'Dashboard':
        show_dashboard()
    elif page == 'Event Management':
        show_event_management()
    else:
        show_club_registration()

    # Footer with trigger logs
    st.sidebar.markdown('---')
    st.sidebar.subheader('Recent System Logs')
    logs = execute_query("""
        SELECT 'Club' as type, old_value, new_value, change_timestamp 
        FROM club_change_log
        UNION ALL
        SELECT 'Department', old_value, new_value, change_timestamp 
        FROM department_change_log
        UNION ALL
        SELECT 'Event', old_value, new_value, change_timestamp 
        FROM event_change_log
        ORDER BY change_timestamp DESC
        LIMIT 5
    """, fetch=True)

    if logs:
        for log in logs:
            st.sidebar.text(f"{log['type']} Change: {log['old_value']} → {log['new_value']}")
            st.sidebar.text(f"Time: {log['change_timestamp']}")
            st.sidebar.markdown('---')