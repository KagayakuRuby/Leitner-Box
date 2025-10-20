import psycopg2
from datetime import datetime

import time

#Change Username and password!
def get_connection():
    return psycopg2.connect(
        dbname="LeitnerBox",
        user="postgres",
        password="138654",
        host="localhost",
        port="5432"
    )

#==================== Login Panel =============== # Ruby
def register():
    conn = get_connection()
    cur = conn.cursor()

    while True:
        username = input("Please enter your username to register: ")

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
            "INSERT INTO users(username, password_hash) VALUES(%s, %s);",
            (username, password)
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

current_user_id = None        
def login(): # Ruby
    global current_user_id, current_username
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password_hash=%s LIMIT 1;", (username, password))
        user = cur.fetchone()
        if user:
            current_user_id = user[0]      
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
    global current_user_id
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:          
        user_id = current_user_id
        
        # finding leitner box id
        cur.execute("SELECT id FROM leitner_boxes WHERE user_id = %s", (user_id,))
        box_result = cur.fetchone()
        
        if not box_result:
            print("❌ You don't have any Leitner Box yet!")
            return
            
        box_id = box_result[0]
        
        # showing the number of the cards for each slot
        print("\n" + "="*40)
        print("📦 YOUR LEITNER BOX")
        print("="*40)
        
        for slot in range(1, 7):
            cur.execute("""
                SELECT COUNT(*) FROM cards 
                WHERE box_id = %s AND current_slot = %s
            """, (box_id, slot))
            count = cur.fetchone()[0]
            
            review_freq = {
                1: "Every day",
                2: "Every 3 days", 
                3: "Every 7 days",
                4: "Every 14 days",
                5: "Every 30 days",
                6: "Learned cards!"
            }
            
            print(f"Slot {slot} ({review_freq[slot]}): {count} cards")
        
        # chosing slot
        while True:
            slot_choice = input("\nEnter slot number to view cards (1-6) or 'menu' to exit: ")
            
            if slot_choice == 'menu':
                return
                
            if slot_choice.isdigit() and 1 <= int(slot_choice) <= 6:
                slot_num = int(slot_choice)
                
                # showing the slot cards that user wanted
                cur.execute("""
                    SELECT question, answer, next_review_date FROM cards 
                    WHERE box_id = %s AND current_slot = %s
                    ORDER BY next_review_date
                """, (box_id, slot_num))
                
                cards = cur.fetchall()
                
                if not cards:
                    print(f"\n📭 Slot {slot_num} is empty!")
                    continue
                
                print(f"\n" + "="*50)
                print(f"📋 SLOT {slot_num} CARDS - {len(cards)} cards")
                print("="*50)
                
                for i, (question, answer, next_review) in enumerate(cards, 1):
                    print(f"[{i}] - {question} :: {answer}")
                    print(f"    Next review: {next_review}")
                    print()
                
                print("="*50)
                print("Enter 'menu' to go back to main menu")
                
                while True:
                    back_input = input()
                    if back_input == 'menu':
                        break
                    else:
                        print("Type 'menu' to exit")
                
                break
            else:
                print("❌ Invalid slot number! Please enter 1-6 or 'menu' to exit")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            conn.close()

def addcard():
    global current_user_id
        
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # get info from user
        card_input = input('Enter your card info like: "Question :: Answer": ')
        
        if " :: " not in card_input:
            print("❌ Invalid format! Use 'Question :: Answer'")
            return
            
        question, answer = card_input.split(" :: ", 1)
            
        user_id = current_user_id
        
        # find or make a leitner box for user
        cur.execute("SELECT id FROM leitner_boxes WHERE user_id = %s", (user_id,))
        box_result = cur.fetchone()
        
        if box_result:
            box_id = box_result[0]
            print(f"✅ Using your existing Leitner Box (ID: {box_id})")
        else:
            print("\n=== Create New Leitner Box ===")
            box_title = input("Enter box title: ").strip()
            box_description = input("Enter box description: ").strip()
            
            # making new leitner box
            cur.execute("""
                INSERT INTO leitner_boxes (user_id, title, description, created_at) 
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (user_id, box_title, box_description, datetime.now()))
            box_id = cur.fetchone()[0]
            print(f"✅ New Leitner Box created with ID: {box_id}")
    
        # add the card to the box
        cur.execute("""
            INSERT INTO cards (box_id, question, answer, current_slot, next_review_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (box_id, question, answer, 1, datetime.now().date()))
        
        conn.commit()
        print("✅ Card added successfully to Slot 1!")
        
    except Exception as e:
        print(f"❌ Error adding card: {e}")
    finally:
        if conn:
            conn.close()

def modifycard():
    pass

def reviewcard():
    pass

def logout(): #Ruby
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
