import streamlit as st
import mysql.connector
from config.db_config import get_connection

def main():
    # Check login
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in first (go to the '1_Login' page).")
        return
    
    st.title(f"Welcome, {st.session_state['user_name']}!")
    st.subheader("View & Filter Listings")

    city_filter = st.text_input("City (optional)")
    min_price = st.number_input("Min Price", value=0, step=50)
    max_price = st.number_input("Max Price", value=2000, step=50)

    if st.button("Search Listings"):
        listings = filter_listings(city_filter, min_price, max_price)
        if listings:
            st.write(f"Found {len(listings)} listing(s).")
            for row in listings:
                st.write(f"**Listing ID**: {row['listing_id']}")
                st.write(f"**Owner**: {row['owner_name']} (Email: {row['owner_email']})")
                st.write(f"**Address**: {row['address']}, {row['city']} {row['state']}, {row['zipcode']}")
                st.write(f"**Rooms**: {row['bedrooms']} bed / {row['bathrooms']} bath")
                st.write(f"**Price**: ${row['price_per_month']}")
                st.write(f"**Available**: {row['available_from']} to {row['available_to']}")
                st.write("---")
        else:
            st.info("No listings found.")

def filter_listings(city, min_price, max_price):
    """
    Prepared statement: fetch listing + apartment + user info
    with optional city filter, and price range.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT L.listing_id,
                   U.name AS owner_name,
                   U.email AS owner_email,
                   A.address,
                   A.city,
                   A.state,
                   A.zipcode,
                   A.bedrooms,
                   A.bathrooms,
                   L.price_per_month,
                   L.available_from,
                   L.available_to
            FROM Listings L
            JOIN Apartments A ON L.apartment_id = A.apartment_id
            JOIN Users U ON A.user_id = U.user_id
            WHERE L.price_per_month BETWEEN %s AND %s
        """
        params = [min_price, max_price]

        if city:
            query += " AND A.city LIKE %s"
            params.append(f"%{city}%")

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except mysql.connector.Error as e:
        st.error(f"DB Error: {e}")
        return []

if __name__ == "__main__":
    main()
