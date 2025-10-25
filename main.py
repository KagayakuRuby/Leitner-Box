import psycopg2
from datetime import date, timedelta

import time
import os

current_user_id = None
current_box_id = None

#Change Username and password!
def get_connection():
    return psycopg2.connect(
        dbname="leitnerbox",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )

#==================== Login Panel =============== # Ruby
def register():
    conn = get_connection()
    cur = conn.cursor()

    while True:
        username = input("Please enter your username to register: ")
        username = username.lower()
        # print(username)

        cur.execute("SELECT 1 FROM users WHERE username = %s;", (username,))
        if cur.fetchone():
            print("Username already exists! Please choose a different one.")
            continue  
        else:
            break 

    while True:
        password = input("Please enter your password: ")
        confirm_password = input("Please confirm your password: ")

        if password != confirm_password:
            print("Passwords do not match! Try again.")
            continue
        else:
            break

    try:
        cur.execute(
            "INSERT INTO users(username, password_hash) VALUES(%s, %s) RETURNING id;",
            (username, password)
        )
        user_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO leitner_boxes(user_id, title) VALUES(%s, %s);",
            (user_id, "Main Box")
        )
        conn.commit()
        print("User registered successfully!")
    except Exception as e:
        print(f"User registration failed! Error: {e}")
    finally:
        if conn:
            conn.close()
        
    #=============== It doesn’t check if the username already exists, so it gives an error. Ruby
    # while True:
    #     username = input("Please enter your username to register: ")

    #     password = input("Please enter your password: ")
    #     confirm_password = input("Please confirm your password: ")

    #     if password != confirm_password:
    #         print("Passwords do not match! Try again.")
    #         continue 
    #     break

    # conn = None
    # try:
    #     conn = get_connection()
    #     cur = conn.cursor()
    #     cur.execute("INSERT INTO users(username, password_hash) VALUES(%s, %s);",
    #                 (username, password))
    #     conn.commit()
    #     print("User registered successfully!")
    # except Exception as e:
    #     print(f"User registration failed! Error: {e}")
    # finally:
    #     if conn:
    #         conn.close()

        
def login(): # Ruby
    global current_user_id, current_box_id
    
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")

    username = username.lower()

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, b.id
            FROM users u
            JOIN leitner_boxes b ON u.id = b.user_id
            WHERE u.username = %s AND u.password_hash = %s
            LIMIT 1;
        """, (username, password))
        user = cur.fetchone()
        if user:
            current_user_id, current_box_id = user
            print(f"✅ Welcome back, {username}!")
            dashbord()
        else:
            print("❌ Username or password is invalid!")
    except Exception as e:
        print("Username or Password is invalid!")
    finally:
        if conn:conn.close()

#============== Dashbord Pannel =============
def showbox():
    """قسمت باکس ها"""
    pass

def addcard():
    pass

def modifycard():
    pass

def calculate_next_review(slot):
    """Calculate next review date based on Leitner slot rules."""
    intervals = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30, 6: 36500}
    return date.today() + timedelta(days=intervals[slot])

def reviewcard():
    """
    Review Card feature:
    - User selects a slot (1-6) by desire.
    - A random card from that slot is shown.
    - User reveals answer with Enter.
    - If "Yes": move to next slot (max 6)
    - If "No": stay in current slot
    - Also logs review in 'reviews' table.
    """
    global current_box_id

    try:
        slot = int(input("Select a slot to review (1-6): "))
        if not (1 <= slot <= 6):
            print("❌ Invalid slot number!")
            input("Press Enter to continue...")
            return
    except ValueError:
        print("❌ Please enter a number between 1 and 6.")
        input("Press Enter to continue...")
        return

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, question, answer 
            FROM cards 
            WHERE box_id = %s AND current_slot = %s
            ORDER BY RANDOM() 
            LIMIT 1
        """, (current_box_id, slot))
        card = cur.fetchone()

        if not card:
            print(f"📭 No cards in Slot {slot}.")
            input("Press Enter to continue...")
            return

        card_id, question, answer = card
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n❓ Question: {question}")
        input("Press Enter to reveal the answer...")
        print(f"✅ Answer: {answer}\n")

        response = input("Did you learn this card? (y/n): ").strip().lower()
        learned = response in ('y', 'yes')

        if learned:
            new_slot = min(slot + 1, 6)
            print(f"→ Card moved to Slot {new_slot}!")
        else:
            new_slot = slot
            print("→ Card remains in current slot.")

        next_date = calculate_next_review(new_slot)
        cur.execute("""
            UPDATE cards 
            SET current_slot = %s, next_review_date = %s 
            WHERE id = %s
        """, (new_slot, next_date, card_id))

        cur.execute("""
            INSERT INTO reviews (card_id, result) 
            VALUES (%s, %s)
        """, (card_id, learned))

        conn.commit()
        print("✅ Card and review logged successfully.")

    except Exception as e:
        print(f"❌ Error during review: {e}")
    finally:
        cur.close()
        conn.close()

    input("Press Enter to return to Dashboard...")

def logout(): #Ruby
    global current_user_id, current_box_id
    current_user_id = None
    current_box_id = None
    menu()

    
# ====================== UI ====================== #Ruby
def menu():
    while True:
        print("\n--- 📋 Welcom To Login Pannel---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Have Good Time :)")
            time.sleep(1.0)
            exit()
        else:
            print("❌ Invalid choice!")

def dashbord():
    while True:
        print("\n--- 📋 Welcom To Dashbord Pannel ---")
        print("1. Show Box")
        print("2. Add Card")
        print("3. Modify Card")
        print("4. Review Card")
        print("5. Logout")

        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            showbox()
        elif choice == "2":
            addcard()
        elif choice == "3":
            modifycard()
        elif choice == "4":
            reviewcard()
        elif choice == "5":
            logout()
        else:
            print("❌ Invalid choice!")


if __name__ == "__main__":
    menu()
