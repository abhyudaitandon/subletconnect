import streamlit as st
import mysql.connector
from config.db_config import get_connection

def login_signup_page():
    st.title("Login / Sign-Up")

    mode = st.radio("Choose Mode", ["Login", "Sign Up"], horizontal=True)

    if mode == "Sign Up":
        st.subheader("Create an Account")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            signup_user(name, email, password)
    else:
        st.subheader("Log In")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            do_login(email, password)

def signup_user(name, email, password):
    try:
        conn = get_connection()
        conn.start_transaction(isolation_level='SERIALIZABLE')
        cursor = conn.cursor()

        args = [name, email, password, 0]  # last is OUT param
        result = cursor.callproc('SignupUser', args)
        new_id = result[-1]  # the OUT param

        conn.commit()
        cursor.close()
        conn.close()

        if new_id == -1:
            st.error("This email is already in use. Please try another.")
        else:
            st.success("Account created successfully!")
            st.info("You can now switch to Login mode.")

    except mysql.connector.Error as e:
        st.error(f"Error signing up: {e}")

def do_login(email, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        args = [email, password, 0]  # the last is OUT param
        result = cursor.callproc('LoginUser', args)
        user_id = result[-1]  # the OUT param

        conn.commit()
        cursor.close()
        conn.close()

        if user_id == 0:
            st.error("Invalid credentials.")
        else:
            # Retrieve the user's name to greet them properly
            user_name = fetch_user_name(user_id)
            if user_name:
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user_id
                st.session_state["user_name"] = user_name
    except mysql.connector.Error as e:
        st.error(f"Login error: {e}")

def fetch_user_name(user_id):
    """
    Prepared statement to get the user's name from ID
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT name FROM Users WHERE user_id = %s LIMIT 1"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0] if row else None
    except:
        return None

def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state["logged_in"]:
        login_signup_page()
    else:
        st.success(f"You are already logged in as {st.session_state.get('user_name','Unknown')}.")
        st.info("Use the sidebar to navigate pages.")

if __name__ == "__main__":
    main()
