Create DataBase LeitnerBox;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE leitner_boxes (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    box_id INT REFERENCES leitner_boxes(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    current_slot INT DEFAULT 1,              
    next_review_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    card_id INT REFERENCES cards(id) ON DELETE CASCADE,
    reviewed_at TIMESTAMP DEFAULT NOW(),
    result BOOLEAN NOT NULL
);
