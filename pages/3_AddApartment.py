import streamlit as st
import mysql.connector
from config.db_config import get_connection

def main():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in first.")
        return
    
    st.title("Add Apartment")
    st.write(f"Hi, {st.session_state['user_name']}! You can register a new apartment here.")

    address = st.text_input("Address")
    city = st.text_input("City")
    state = st.text_input("State")
    zipcode = st.text_input("Zip Code")
    bedrooms = st.number_input("Bedrooms", min_value=0, max_value=10)
    bathrooms = st.number_input("Bathrooms", min_value=0, max_value=10)

    if st.button("Add Apartment"):
        success = add_apartment(st.session_state["user_id"], address, city, state, zipcode, bedrooms, bathrooms)
        if success:
            st.success("Apartment added successfully!")
        else:
            st.error("Failed to add apartment. Check logs or DB connection.")

def add_apartment(user_id, address, city, state, zipcode, beds, baths):
    """
    Prepared statement to insert a row into Apartments.
    The 'user_id' references the owner of that apartment.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO Apartments(user_id, address, city, state, zipcode, bedrooms, bathrooms)
            VALUES(%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, address, city, state, zipcode, beds, baths))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as e:
        st.error(f"DB Error: {e}")
        return False

if __name__ == "__main__":
    main()
