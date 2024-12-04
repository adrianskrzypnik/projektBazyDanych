-- CREATE TABLE users (
--     user_id INT AUTO_INCREMENT PRIMARY KEY,
--     nazwa VARCHAR(255) NOT NULL,
--     email VARCHAR(255) NOT NULL,
--     haslo VARCHAR(255) NOT NULL,
--     data_utworzenia DATE
-- );

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    nazwa VARCHAR(255) NOT NULL
);

CREATE TABLE ads (
    ad_id INT AUTO_INCREMENT PRIMARY KEY,
    tytul VARCHAR(255) NOT NULL,
    opis TEXT,
    cena DECIMAL(10, 2),
    kategoria_id INT,
    uzytkownik_id INT,
    status BOOLEAN DEFAULT TRUE,
    data_utworzenia DATE,
    FOREIGN KEY (kategoria_id) REFERENCES categories(category_id),
    FOREIGN KEY (uzytkownik_id) REFERENCES users(user_id)
);

CREATE TABLE comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    ogloszenie_id INT,
    uzytkownik_id INT,
    tresc TEXT,
    data_utworzenia DATE,
    FOREIGN KEY (ogloszenie_id) REFERENCES ads(ad_id),
    FOREIGN KEY (uzytkownik_id) REFERENCES users(user_id)
);

CREATE TABLE likes (
    like_id INT AUTO_INCREMENT PRIMARY KEY,
    ogloszenie_id INT,
    uzytkownik_id INT,
    polubiony_przez INT,
    FOREIGN KEY (ogloszenie_id) REFERENCES ads(ad_id),
    FOREIGN KEY (uzytkownik_id) REFERENCES users(user_id)
);

CREATE TABLE ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    oceniający_id INT,
    oceniany_id INT,
    ocena INT,
    data_oceny DATE,
    FOREIGN KEY (oceniający_id) REFERENCES users(user_id),
    FOREIGN KEY (oceniany_id) REFERENCES users(user_id)
);
