import streamlit as st
from db_config import test_connection

def main():
    st.title("Database Connection Test")
    if st.button("Test Connection"):
        if test_connection():
            st.success("Successfully connected to the database!")
        else:
            st.error("Failed to connect to the database")

if __name__ == "__main__":
    main()