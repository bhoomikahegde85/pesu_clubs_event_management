import streamlit as st
import mysql.connector
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
import pandas as pd
from contextlib import contextmanager
import re

# Data classes for type safety and better structure
@dataclass
class User:
    email: str
    role: str

@dataclass
class Club:
    name: str
    email: str
    instagram_handle: str
    department_name: str
    faculty_advisor: str
    department_id: str
    advisor_srn: str

@dataclass
class Event:
    event_id: int
    title: str
    start_date: datetime
    location: str
    budget: float
    duration: int
    club_name: str

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'pesu_clubs_event_management',
    'user': 'root',
    'password': 'harryzayn1d',
}

class DatabaseManager:
    @staticmethod
    def get_role_specific_connection(role: Optional[str] = None) -> Dict[str, str]:
        """Get role-specific database configuration"""
        config = DB_CONFIG.copy()
        
        role_configs = {
            'club_head': ('club_head', 'ClubHead@123'),
            'management': ('management', 'Management@123'),
            'club_member': ('viewer', 'Viewer@123'),
            'viewer': ('viewer', 'Viewer@123'),
            None: ('viewer', 'Viewer@123')
        }
        
        if role in role_configs:
            user, password = role_configs[role]
            config.update({'user': user, 'password': password})
            
        return config

    @staticmethod
    @contextmanager
    def get_connection(role: Optional[str] = None):
        """Context manager for database connections with role-specific permissions"""
        config = DatabaseManager.get_role_specific_connection(role)
        conn = None
        try:
            conn = mysql.connector.connect(**config)
            yield conn
        except mysql.connector.Error as err:
            st.error(f"Database error: {err}")
            yield None
        finally:
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def execute_query(query: str, params: tuple = None, commit: bool = False, role: Optional[str] = None) -> Optional[List[Tuple]]:
        """Execute database query with role-specific permissions"""
        with DatabaseManager.get_connection(role) as conn:
            if not conn:
                return None
                
            cursor = conn.cursor(buffered=True)
            try:
                cursor.execute(query, params or ())
                
                if commit:
                    conn.commit()
                    return cursor.rowcount if cursor.rowcount > 0 else None
                return cursor.fetchall()
            except mysql.connector.Error as err:
                st.error(f"Query error: {err}")
                return None
            finally:
                cursor.close()

class AuthManager:
    @staticmethod
    def login(username: str, password: str) -> Optional[str]:
        """Authenticate user and return their role if successful"""
        if not username or not password:
            st.error("Please enter both username and password.")
            return None

        result = DatabaseManager.execute_query(
            "SELECT role FROM users WHERE email = %s AND password = %s",
            (username, password)
        )
        return result[0][0] if result else None

    @staticmethod
    def validate_permission(required_roles: List[str], current_role: str) -> bool:
        """Validate if current role has required permissions"""
        if not current_role or current_role not in required_roles:
            st.error("You don't have permission to perform this action")
            return False
        return True

class ClubManager:
    @staticmethod
    def get_user_club(email: str) -> Optional[str]:
        """Get the club name associated with a club head"""
        result = DatabaseManager.execute_query(
            """
            SELECT club_name 
            FROM CLUB_HEAD_ASSOCIATION 
            WHERE email = %s
            """,
            (email,)
        )
        return result[0][0] if result else None

    @staticmethod
    def can_edit_club(user_email: str, club_name: str) -> bool:
        """Check if user has permission to edit the club"""
        if st.session_state.user_role == 'management':
            return True
        
        if st.session_state.user_role == 'club_head':
            result = DatabaseManager.execute_query(
                """
                SELECT 1 
                FROM CLUB_HEAD_ASSOCIATION 
                WHERE email = %s AND club_name = %s
                """,
                (user_email, club_name)
            )
            return bool(result)
            
        return False

    @staticmethod
    def validate_club_data(club_email: str, instagram_handle: str) -> bool:
        """Validate club update data"""
        if not club_email:
            st.error("Club email is required.")
            return False
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", club_email):
            st.error("Please enter a valid email address.")
            return False
            
        return True

    @staticmethod
    def get_clubs(search_query: Optional[str] = None) -> List[Club]:
        """Fetch clubs with optional search"""
        query = """
            SELECT c.club_name, c.club_email, c.instagram_handle, d.depart_id, 
                   f.SRN, d.department_name, f.name as faculty_advisor
            FROM CLUB c
            JOIN DEPARTMENT d ON c.depart_id = d.depart_id
            JOIN FACULTY_ADVISOR f ON c.faculty_advisor_srn = f.SRN
        
        """
        
        params = []
        conditions = []
        
        # Handle club head restrictions
        if st.session_state.user_role == 'club_head':
            conditions.append("c.club_name IN (SELECT club_name FROM CLUB_HEAD_ASSOCIATION WHERE email = %s)")
            params.append(st.session_state.user_email)
        
        # Handle search
        if search_query:
            conditions.append("(c.club_name LIKE %s OR d.department_name LIKE %s)")
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        results = DatabaseManager.execute_query(query, tuple(params))
        
        return [
            Club(
                name=row[0],
                email=row[1],
                instagram_handle=row[2],
                department_id=row[3],
                advisor_srn=row[4],
                department_name=row[5],
                faculty_advisor=row[6]
            ) for row in (results or [])
        ]

    @staticmethod
    def update_club(club_name: str, club_email: str, instagram_handle: str, user_email: str) -> bool:
        """Update club details"""
        try:
            # Check permissions
            if not ClubManager.can_edit_club(user_email, club_name):
                st.error("You don't have permission to edit this club.")
                return False
                
            # Validate input data
            if not ClubManager.validate_club_data(club_email, instagram_handle):
                return False
                
            # Execute update
            result = DatabaseManager.execute_query(
                """
                UPDATE CLUB 
                SET club_email = %s, instagram_handle = %s
                WHERE club_name = %s
                """,
                (club_email, instagram_handle, club_name),
                commit=True,
                role=st.session_state.user_role
            )
            
            if result:
                st.success(f"Successfully updated {club_name}")
                return True
            else:
                st.error(f"Failed to update {club_name}. No changes were made.")
                return False
                
        except Exception as e:
            st.error(f"An error occurred while updating the club: {str(e)}")
            return False

class Dashboard:
    def __init__(self):
        self.initialize_session_state()
        
    @staticmethod
    def initialize_session_state():
        """Initialize session state variables"""
        initial_states = {
            'logged_in': False,
            'user_role': None,
            'user_email': None,
            'selected_club': None,
            'edit_event': None,
            'show_edit_form': False
        }
        
        for key, value in initial_states.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def render_login(self):
        """Render login form"""
        with st.sidebar:
            if not st.session_state.logged_in:
                st.header("Login")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.button("Login"):
                    role = AuthManager.login(username, password)
                    if role:
                        st.session_state.logged_in = True
                        st.session_state.user_role = role
                        st.session_state.user_email = username
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            else:
                st.write(f"Logged in as: {st.session_state.user_role}")
                if st.button("Logout"):
                    for key in st.session_state.keys():
                        del st.session_state[key]
                    self.initialize_session_state()
                    st.rerun()

    def render_stats(self):
        """Render dashboard statistics"""
        st.subheader("Quick Stats")
        col1, col2 = st.columns(2)
        
        with col1:
            results = DatabaseManager.execute_query(
                "SELECT COUNT(*) FROM CLUB UNION ALL SELECT COUNT(*) FROM EVENT"
            )
            if results:
                st.metric("Total Clubs", results[0][0])
                st.metric("Total Events", results[1][0])

    def render_club_edit_form(self, club: Club):
        """Render the club edit form"""
        with st.form(key=f"edit_club_form_{club.name}"):
            st.subheader(f"Edit {club.name}")
            new_email = st.text_input("Club Email", value=club.email)
            new_instagram = st.text_input("Instagram Handle", value=club.instagram_handle or "")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                submit = st.form_submit_button("Update Club")
            with col2:
                cancel = st.form_submit_button("Cancel")
                
            if submit:
                if ClubManager.update_club(
                    club.name, 
                    new_email, 
                    new_instagram,
                    st.session_state.user_email
                ):
                    st.session_state.show_edit_form = False
                    st.rerun()
            elif cancel:
                st.session_state.show_edit_form = False
                st.rerun()

    def render_club_directory(self):
        """Render club directory with search"""
        st.subheader("Club Directory")
        search_query = st.text_input("Search clubs by name or department...")
        clubs = ClubManager.get_clubs(search_query if search_query else None)
        
        if not clubs:
            st.info("No clubs found matching your search criteria.")
            return
            
        cols = st.columns(2)
        for idx, club in enumerate(clubs):
            with cols[idx % 2]:
                with st.container():
                    with st.expander(f"📚 {club.name}", expanded=False):
                        st.markdown(f"**Department:** {club.department_name}")
                        st.markdown(f"**Faculty Advisor:** {club.faculty_advisor}")
                        st.markdown(f"**Email:** {club.email}")
                        
                        if club.instagram_handle:
                            st.markdown(f"**Instagram:** {club.instagram_handle}")
                        
                        if ClubManager.can_edit_club(st.session_state.user_email, club.name):
                            if st.button("Edit Details", key=f"edit_{club.name}"):
                                st.session_state.show_edit_form = True
                                st.session_state.selected_club = club
                                st.rerun()
                st.divider()
        
        # Render edit form if needed
        if st.session_state.show_edit_form and st.session_state.selected_club:
            self.render_club_edit_form(st.session_state.selected_club)

    def render_dashboard(self):
        """Render main dashboard"""
        st.title("PESU Club and Event Management System")
        
        tab1, tab2 = st.tabs(["Dashboard", "Club Directory"])
        
        with tab1:
            self.render_stats()
            
        with tab2:
            self.render_club_directory()

def main():
    st.set_page_config(
        page_title="PESU Club Management",
        page_icon="🎓",
        layout="wide"
    )
    
    dashboard = Dashboard()
    dashboard.render_login()
    
    if st.session_state.logged_in:
        dashboard.render_dashboard()
    else:
        st.info("Please log in to access the system.")

if __name__ == "__main__":
    main()