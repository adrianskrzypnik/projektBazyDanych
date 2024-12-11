CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    nazwa VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    data_utworzenia DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE
);


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

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    target_type VARCHAR(10) NOT NULL CHECK (target_type IN ('ad', 'user')),
    ad_id INT NULL,
    target_user_id INT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (ad_id) REFERENCES ads(ad_id),
    FOREIGN KEY (target_user_id) REFERENCES users(user_id),
    CONSTRAINT target_check CHECK (
        (ad_id IS NOT NULL AND target_user_id IS NULL AND target_type = 'ad') OR
        (ad_id IS NULL AND target_user_id IS NOT NULL AND target_type = 'user')
    )
);


CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,  -- użytkownik, który daje polubienie
    target_type VARCHAR(10) NOT NULL CHECK (target_type IN ('ad', 'user')),
    ad_id INT NULL,
    target_user_id INT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (ad_id) REFERENCES ads(ad_id),
    FOREIGN KEY (target_user_id) REFERENCES users(user_id),
    UNIQUE(user_id, target_type, ad_id, target_user_id)
);

CREATE TABLE ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    oceniajacy_id INT,
    oceniany_id INT,
    ocena INT,
    data_oceny DATE,
    FOREIGN KEY (oceniajacy_id) REFERENCES users(user_id),
    FOREIGN KEY (oceniany_id) REFERENCES users(user_id)
);
