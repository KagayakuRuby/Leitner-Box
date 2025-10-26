
DROP TABLE IF EXISTS users CASCADE;
-- جدول کاربران
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);


DROP TABLE IF EXISTS categories CASCADE;
-- جدول دسته‌بندی‌ها
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);


DROP TABLE IF EXISTS cards CASCADE;
-- جدول کارت‌ها
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    category_id INTEGER REFERENCES categories(id),
    front_text TEXT NOT NULL,
    back_text TEXT NOT NULL,
    current_box INTEGER DEFAULT 1,
    next_review_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW()
);



SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
