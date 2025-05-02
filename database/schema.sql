-- Drop existing tables (helpful for dev)
DROP TABLE IF EXISTS Listings;
DROP TABLE IF EXISTS Apartments;
DROP TABLE IF EXISTS Users;

-- Users: storing plain text passwords (no hashing, per your request).
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Apartments (
    apartment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,  -- the owner of the apartment
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    zipcode VARCHAR(10),
    bedrooms INT,
    bathrooms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Listings (
    listing_id INT AUTO_INCREMENT PRIMARY KEY,
    apartment_id INT NOT NULL,
    price_per_month DECIMAL(10, 2) NOT NULL,
    available_from DATE NOT NULL,
    available_to DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (apartment_id) REFERENCES Apartments(apartment_id) ON DELETE CASCADE
);
