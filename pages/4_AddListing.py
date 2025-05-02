import streamlit as st
import mysql.connector
from config.db_config import get_connection
from datetime import date

def main():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in first.")
        return

    st.title("Add Listing")
    st.write(f"Hello, {st.session_state['user_name']}! Create a listing from one of your apartments below.")

    # 1) Fetch all apartments owned by the current user
    user_id = st.session_state["user_id"]
    apartments = get_user_apartments(user_id)
    if not apartments:
        st.info("You have no apartments. Please add one first on the '3_AddApartment' page.")
        return

    # 2) Let them pick an apartment
    apt_choices = {f"{apt['apartment_id']} - {apt['address']}": apt['apartment_id'] for apt in apartments}
    chosen_label = st.selectbox("Select Apartment", list(apt_choices.keys()))
    chosen_apartment_id = apt_choices[chosen_label]

    # 3) Fill listing details
    price = st.number_input("Monthly Price", min_value=0.0, step=50.0, value=500.0)
    from_date = st.date_input("Available From", value=date.today())
    to_date = st.date_input("Available To", value=date.today())
    description = st.text_area("Description")

    if st.button("Create Listing"):
        create_listing(chosen_apartment_id, price, from_date, to_date, description)

def get_user_apartments(user_id):
    """
    Prepared statement to get all apartments owned by this user.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT apartment_id, address
            FROM Apartments
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except mysql.connector.Error as e:
        st.error(f"DB Error: {e}")
        return []

def create_listing(apartment_id, price, from_date, to_date, desc):
    """
    Calls stored procedure: CreateListing(...) 
    which returns new listing ID in an OUT param.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        args = [apartment_id, price, from_date, to_date, desc, 0]  # 0 is placeholder for OUT
        result = cursor.callproc('CreateListing', args)
        new_id = result[-1]  # the OUT param

        conn.commit()
        cursor.close()
        conn.close()

        st.success(f"Listing created successfully! ID = {new_id}")
    except mysql.connector.Error as e:
        st.error(f"CreateListing error: {e}")

if __name__ == "__main__":
    main()
