
-- 1. مشاهده کارت‌ها (READ)
-- دیدن همه کارت‌های یک کاربر
CREATE OR REPLACE FUNCTION get_user_cards(user_id INTEGER)
RETURNS TABLE(
    card_id INTEGER,
    front TEXT,
    back TEXT,
    box INTEGER,
    review_date DATE,
    category VARCHAR,
    created_time TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.front_text,
        c.back_text,
        c.current_box,
        c.next_review_date,
        cat.name,
        c.created_at
    FROM cards c
    LEFT JOIN categories cat ON c.category_id = cat.id
    WHERE c.user_id = get_user_cards.user_id
    ORDER BY c.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- 2. آپدیت کردن یک کارت
CREATE OR REPLACE FUNCTION update_card(
    card_id INTEGER,
    user_id INTEGER,
    new_front TEXT DEFAULT NULL,
    new_back TEXT DEFAULT NULL,
    new_category INTEGER DEFAULT NULL,
    new_box INTEGER DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE cards 
    SET 
        front_text = COALESCE(new_front, front_text),
        back_text = COALESCE(new_back, back_text),
        category_id = COALESCE(new_category, category_id),
        current_box = COALESCE(new_box, current_box),
        updated_at = NOW()
    WHERE id = card_id AND user_id = update_card.user_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;



-- 3. حذف کارت (DELETE)
CREATE OR REPLACE FUNCTION delete_card(
    card_id INTEGER,
    user_id INTEGER
) RETURNS BOOLEAN AS $$
BEGIN
    DELETE FROM cards 
    WHERE id = card_id AND user_id = delete_card.user_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- 4. جستجوی کارت‌ها
CREATE OR REPLACE FUNCTION search_cards(
    user_id INTEGER,
    search_text TEXT DEFAULT NULL
) RETURNS TABLE(
    card_id INTEGER,
    front TEXT,
    back TEXT,
    box INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.front_text,
        c.back_text,
        c.current_box
    FROM cards c
    WHERE c.user_id = search_cards.user_id
    AND (search_text IS NULL OR c.front_text ILIKE '%' || search_text || '%')
    ORDER BY c.created_at DESC;
END;
$$ LANGUAGE plpgsql;



-- 5. ایجاد دسته‌بندی جدید
CREATE OR REPLACE FUNCTION create_category(
    user_id INTEGER,
    name VARCHAR(100),
    description TEXT DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    new_category_id INTEGER;
BEGIN
    INSERT INTO categories (user_id, name, description)
    VALUES (user_id, name, description)
    RETURNING id INTO new_category_id;
    
    RETURN new_category_id;
END;
$$ LANGUAGE plpgsql;

-- 6. تغییر دسته‌بندی کارت‌ها
CREATE OR REPLACE FUNCTION change_cards_category(
    user_id INTEGER,
    old_category_id INTEGER,
    new_category_id INTEGER
) RETURNS INTEGER AS $$
BEGIN
    UPDATE cards 
    SET category_id = new_category_id,
        updated_at = NOW()
    WHERE user_id = change_cards_category.user_id
    AND category_id = old_category_id;
    
    RETURN 1;
END;
$$ LANGUAGE plpgsql;


-- 7. نمایش دسته‌بندی‌ها
SELECT id, name, description 
FROM categories 
WHERE user_id = 1 
ORDER BY name;
