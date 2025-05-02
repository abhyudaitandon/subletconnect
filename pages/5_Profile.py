import streamlit as st
import mysql.connector
from config.db_config import get_connection
from datetime import date

def main():
    # Ensure user is logged in
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in first.")
        return

    st.title("Your Profile")
    st.subheader(f"Hello, {st.session_state['user_name']}!")

    # 1. EDIT USER INFO
    edit_user_info()

    st.write("---")

    # 2. MANAGE APARTMENTS (edit, delete)
    manage_user_apartments()

    st.write("---")

    # 3. MANAGE LISTINGS (edit, delete)
    manage_user_listings()

########################################
# 1) EDIT USER INFO
########################################
def edit_user_info():
    st.write("## Update Your Name/Email")

    # Fetch current user info
    user_id = st.session_state["user_id"]
    user_details = get_user_details(user_id)
    if not user_details:
        st.error("Could not load user details.")
        return

    current_name, current_email = user_details
    new_name = st.text_input("Name", value=current_name)
    new_email = st.text_input("Email", value=current_email)

    if st.button("Save User Info"):
        if update_user_info(user_id, new_name, new_email):
            st.success("User info updated successfully!")
            # Update session state so name is shown everywhere
            st.session_state["user_name"] = new_name
        else:
            st.error("Failed to update user info.")

def get_user_details(user_id):
    """Prepared statement to fetch user's current name, email."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT name, email FROM Users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row if row else None
    except mysql.connector.Error as e:
        st.error(f"get_user_details error: {e}")
        return None

def update_user_info(user_id, name, email):
    """Prepared statement to update user's name and email."""
    try:
        conn = get_connection()
        conn.start_transaction(isolation_level='REPEATABLE READ')
        cursor = conn.cursor()
        query = "UPDATE Users SET name=%s, email=%s WHERE user_id=%s"
        cursor.execute(query, (name, email, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as e:
        st.error(f"update_user_info error: {e}")
        return False

########################################
# 2) MANAGE APARTMENTS
########################################
def manage_user_apartments():
    st.write("## Your Apartments")

    user_id = st.session_state["user_id"]
    apartments = get_user_apartments(user_id)

    if not apartments:
        st.info("You have no apartments. Add one on the 'Add Apartment' page.")
        return

    # Let user pick an apartment from a dropdown
    apt_labels = {f"{a['apartment_id']} - {a['address']}": a for a in apartments}
    chosen_label = st.selectbox("Select an Apartment to Edit/Delete", list(apt_labels.keys()))
    chosen_apartment = apt_labels[chosen_label]

    # Show editable fields
    addr = st.text_input("Address", value=chosen_apartment["address"])
    city = st.text_input("City", value=chosen_apartment["city"])
    state = st.text_input("State", value=chosen_apartment["state"])
    zipcode = st.text_input("Zip Code", value=chosen_apartment["zipcode"] or "")
    bedrooms = st.number_input("Bedrooms", min_value=0, max_value=10, value=chosen_apartment["bedrooms"] or 0)
    bathrooms = st.number_input("Bathrooms", min_value=0, max_value=10, value=chosen_apartment["bathrooms"] or 0)

    if st.button("Update Apartment"):
        success = update_apartment(
            chosen_apartment["apartment_id"],
            addr, city, state, zipcode, bedrooms, bathrooms
        )
        if success:
            st.success("Apartment updated successfully!")
            st.rerun()  # Refresh the page to reflect changes
        else:
            st.error("Failed to update apartment.")

    if st.button("Delete Apartment"):
        # Deleting an apartment will also cascade delete associated listings
        # per your ON DELETE CASCADE constraint
        success = delete_apartment(chosen_apartment["apartment_id"])
        if success:
            st.success("Apartment deleted successfully!")
            st.rerun()
        else:
            st.error("Failed to delete apartment.")

def get_user_apartments(user_id):
    """Prepared statement to fetch all apartments for this user."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT apartment_id, address, city, state, zipcode, bedrooms, bathrooms
            FROM Apartments
            WHERE user_id=%s
            ORDER BY apartment_id
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as e:
        st.error(f"get_user_apartments error: {e}")
        return []

def update_apartment(apartment_id, address, city, state, zipcode, bedrooms, bathrooms):
    """Prepared statement to update an apartment row."""
    try:
        conn = get_connection()
        conn.start_transaction(isolation_level='REPEATABLE READ')
        cursor = conn.cursor()
        query = """
            UPDATE Apartments
            SET address=%s, city=%s, state=%s, zipcode=%s, bedrooms=%s, bathrooms=%s
            WHERE apartment_id=%s
        """
        cursor.execute(query, (address, city, state, zipcode, bedrooms, bathrooms, apartment_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as e:
        st.error(f"update_apartment error: {e}")
        return False

def delete_apartment(apartment_id):
    """Prepared statement to delete an apartment (and cascade to listings)."""
    try:
        conn = get_connection()
        conn.start_transaction(isolation_level='REPEATABLE READ')
        cursor = conn.cursor()
        query = "DELETE FROM Apartments WHERE apartment_id=%s"
        cursor.execute(query, (apartment_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as e:
        st.error(f"delete_apartment error: {e}")
        return False

########################################
# 3) MANAGE LISTINGS
########################################
def manage_user_listings():
    st.write("## Your Listings")

    # 1) Load all listings (with their current apt_id) that belong to the user
    listings = get_user_listings(st.session_state["user_id"])
    if not listings:
        st.info("You have no listings. Create one on the 'Add Listing' page.")
        return

    # 2) Pick which listing to edit/delete
    lst_labels = {f"Listing {l['listing_id']} - Apt {l['apartment_id']}": l for l in listings}
    chosen_label = st.selectbox("Select a Listing to Edit/Delete", list(lst_labels.keys()))
    chosen_listing = lst_labels[chosen_label]

    # 3) Show listing fields
    price = st.number_input("Price per Month", min_value=0.0, step=50.0, value=float(chosen_listing["price_per_month"]))
    from_date = st.date_input("Available From", value=chosen_listing["available_from"])
    to_date = st.date_input("Available To", value=chosen_listing["available_to"])
    desc = st.text_area("Description", value=chosen_listing["description"] or "")

    # 4) Let user select a different apartment they own
    user_id = st.session_state["user_id"]
    apartments = get_user_apartments(user_id)  # fetch all user-owned apartments
    if not apartments:
        st.warning("You have no apartments. Please create one first.")
        return

    # Create a dict for apartment dropdown
    apt_labels = {f"Apt {a['apartment_id']} - {a['address']}": a for a in apartments}
    # Find the label that matches the listing’s current apt
    default_label = None
    for lbl, data in apt_labels.items():
        if data["apartment_id"] == chosen_listing["apartment_id"]:
            default_label = lbl
            break

    chosen_apt_label = st.selectbox("Apartment for This Listing", list(apt_labels.keys()), index=list(apt_labels.keys()).index(default_label) if default_label else 0)
    chosen_apartment = apt_labels[chosen_apt_label]

    # 5) Buttons for update & delete
    if st.button("Update Listing"):
        success = update_listing(
            listing_id=chosen_listing["listing_id"],
            apartment_id=chosen_apartment["apartment_id"],
            price=price,
            from_date=from_date,
            to_date=to_date,
            desc=desc
        )
        if success:
            st.success("Listing updated successfully!")
            st.rerun()
        else:
            st.error("Failed to update listing.")

    if st.button("Delete Listing"):
        success = delete_listing(chosen_listing["listing_id"])
        if success:
            st.success("Listing deleted successfully!")
            st.rerun()
        else:
            st.error("Failed to delete listing.")

def get_user_listings(user_id):
    """
    Prepared statement to fetch all listings belonging to the user's apartments.
    i.e. The user must own the apt, so we do a JOIN on Apartments->Listings.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT L.listing_id, L.apartment_id, L.price_per_month,
                   L.available_from, L.available_to, L.description
            FROM Listings L
            JOIN Apartments A ON L.apartment_id = A.apartment_id
            WHERE A.user_id = %s
            ORDER BY L.listing_id
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as e:
        st.error(f"get_user_listings error: {e}")
        return []

def update_listing(listing_id, apartment_id, price, from_date, to_date, desc):
    """Prepared statement to update listing details (including apartment_id)."""
    try:
        conn = get_connection()
        conn.start_transaction(isolation_level='REPEATABLE READ')
        cursor = conn.cursor()
        query = """
            UPDATE Listings
            SET apartment_id=%s, 
                price_per_month=%s, 
                available_from=%s, 
                available_to=%s, 
                description=%s
            WHERE listing_id=%s
        """
        cursor.execute(query, (apartment_id, price, from_date, to_date, desc, listing_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as e:
        st.error(f"update_listing error: {e}")
        return False

def delete_listing(listing_id):
    """Prepared statement to delete the listing."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM Listings WHERE listing_id=%s"
        cursor.execute(query, (listing_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as e:
        st.error(f"delete_listing error: {e}")
        return False

def get_user_apartments(user_id):
    """
    Prepared statement to fetch all apartments for the user.
    We return them in dictionary form so we can easily display a label for the user.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT apartment_id, address, city, state, zipcode, bedrooms, bathrooms
            FROM Apartments
            WHERE user_id=%s
            ORDER BY apartment_id
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as e:
        st.error(f"get_user_apartments error: {e}")
        return []

if __name__ == "__main__":
    main()