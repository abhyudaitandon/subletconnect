DROP PROCEDURE IF EXISTS SignupUser;
DELIMITER $$
CREATE PROCEDURE SignupUser(
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_password VARCHAR(100),
    OUT p_new_user_id INT
)
BEGIN
    DECLARE email_count INT DEFAULT 0;
    
    SELECT COUNT(*) INTO email_count
    FROM Users
    WHERE email = p_email;
    
    IF email_count > 0 THEN
        SET p_new_user_id = -1;  -- email in use
    ELSE
        INSERT INTO Users(name, email, password)
        VALUES(p_name, p_email, p_password);
        
        SET p_new_user_id = LAST_INSERT_ID();
    END IF;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS LoginUser;
DELIMITER $$
CREATE PROCEDURE LoginUser(
    IN p_email VARCHAR(100),
    IN p_password VARCHAR(100),
    OUT p_user_id INT
)
BEGIN
    SELECT user_id
    INTO p_user_id
    FROM Users
    WHERE email = p_email
      AND password = p_password
    LIMIT 1;

    IF p_user_id IS NULL THEN
        SET p_user_id = 0;  -- invalid
    END IF;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS CreateListing;
DELIMITER $$
CREATE PROCEDURE CreateListing(
    IN p_apartment_id INT,
    IN p_price DECIMAL(10,2),
    IN p_from DATE,
    IN p_to DATE,
    IN p_description TEXT,
    OUT p_new_listing_id INT
)
BEGIN
    INSERT INTO Listings(apartment_id, price_per_month, available_from, available_to, description)
    VALUES(p_apartment_id, p_price, p_from, p_to, p_description);

    SET p_new_listing_id = LAST_INSERT_ID();
END$$
DELIMITER ;
