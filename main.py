import psycopg2
from datetime import date, timedelta, datetime

import time
import os

current_user_id = None
current_box_id = None

#Change Username and password!
def get_connection():
    return psycopg2.connect(
        dbname="leitnerbox",
        user="postgres",
        password="138654",
        host="localhost",
        port="5432"
    )

#==================== Login Panel =============== # Ruby
def clear_screen():
    """clear screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

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
    time.sleep(2)
    clear_screen()

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
            time.sleep(2) 
            clear_screen()
            dashbord()
        else:
            print("❌ Username or password is invalid!")
            time.sleep(2) 
            clear_screen()
    except Exception as e:
        print(f"Login error: {e}")
        time.sleep(2)
        clear_screen()
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
    input("Press Enter to continue...")
    clear_screen()
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
    input("Press Enter to continue...")
    clear_screen()
    
def modifycard():
    global current_user_id
    
    if current_user_id is None:
        print("❌ Please login first!")
        return
        
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM leitner_boxes WHERE user_id = %s", (current_user_id,))
        box_result = cur.fetchone()
        
        if not box_result:
            print("❌ You don't have any Leitner Box yet!")
            return
            
        box_id = box_result[0]
        
        slot_choice = input("Enter slot number (1-6) to modify cards: ")
        if not slot_choice.isdigit() or not 1 <= int(slot_choice) <= 6:
            print("❌ Invalid slot number!")
            return
            
        slot_num = int(slot_choice)
        
        cur.execute("""
            SELECT id, question, answer FROM cards 
            WHERE box_id = %s AND current_slot = %s
            ORDER BY id
        """, (box_id, slot_num))
        
        cards = cur.fetchall()
        
        if not cards:
            print(f"📭 No cards in Slot {slot_num}")
            return
            
        print(f"\n=== Cards in Slot {slot_num} ===")
        for i, (card_id, question, answer) in enumerate(cards, 1):
            print(f"[{i}] - {question} :: {answer}")
        
        card_choice = input("\nEnter card number to modify: ")
        if not card_choice.isdigit() or not 1 <= int(card_choice) <= len(cards):
            print("❌ Invalid card number!")
            return
            
        card_id = cards[int(card_choice)-1][0]

        print("\n1. ✏️ Edit Card")
        print("2. 🗑️ Delete Card")
        print("3. ↩️ Cancel")
        
        action = input("Choose action: ")
        
        if action == "1":
            new_input = input('Enter new card info like: "New Question :: New Answer": ')
            if " :: " in new_input:
                new_question, new_answer = new_input.split(" :: ", 1)
                cur.execute("""
                    UPDATE cards SET question = %s, answer = %s 
                    WHERE id = %s
                """, (new_question, new_answer, card_id))
                conn.commit()
                print("✅ Card updated successfully!")
            else:
                print("❌ Invalid format!")
                
        elif action == "2":
            confirm = input("Are you sure you want to delete this card? (y/n): ")
            if confirm.lower() == 'y':
                cur.execute("DELETE FROM reviews WHERE card_id = %s", (card_id,))
                cur.execute("DELETE FROM cards WHERE id = %s", (card_id,))
                conn.commit()
                print("✅ Card deleted successfully!")
            else:
                print("❌ Deletion cancelled!")
                
        elif action == "3":
            print("↩️ Operation cancelled!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            conn.close()
    input("Press Enter to continue...")
    clear_screen()

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
            clear_screen()
            return
    except ValueError:
        print("❌ Please enter a number between 1 and 6.")
        input("Press Enter to continue...")
        clear_screen()
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
            clear_screen()
            return

        card_id, question, answer = card
        clear_screen()
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
    clear_screen()
    


def show_statistics():
    """Show user statistics"""
    global current_user_id
    
    if current_user_id is None:
        print("❌ Please login first!")
        return
        
    clear_screen()
    print("\n" + "="*50)
    print(" 📊 YOUR STATISTICS")
    print("="*50)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get all statistics in one go
        cur.execute("SELECT COUNT(*) FROM cards WHERE box_id IN (SELECT id FROM leitner_boxes WHERE user_id = %s)", (current_user_id,))
        total_cards = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*) FROM cards 
            WHERE box_id IN (SELECT id FROM leitner_boxes WHERE user_id = %s) 
            AND next_review_date <= CURRENT_DATE
        """, (current_user_id,))
        due_cards = cur.fetchone()[0]
        
        cur.execute("""
            SELECT current_slot, COUNT(*) 
            FROM cards 
            WHERE box_id IN (SELECT id FROM leitner_boxes WHERE user_id = %s) 
            GROUP BY current_slot ORDER BY current_slot
        """, (current_user_id,))
        slot_distribution = cur.fetchall()
        
        cur.execute("""
            SELECT COUNT(*), SUM(CASE WHEN result THEN 1 ELSE 0 END) 
            FROM reviews 
            WHERE card_id IN (SELECT id FROM cards WHERE box_id IN (SELECT id FROM leitner_boxes WHERE user_id = %s))
        """, (current_user_id,))
        review_stats = cur.fetchone()
        total_reviews = review_stats[0] if review_stats else 0
        correct_reviews = review_stats[1] if review_stats and review_stats[1] else 0
        
        # Display statistics
        print(f"\n📈 Basic Statistics:")
        print(f"📜 Total Cards: {total_cards}")
        print(f"📚 Due for Review: {due_cards}")
        
        if total_reviews > 0:
            success_rate = (correct_reviews / total_reviews) * 100
            print(f"🎯 Success Rate: {success_rate:.1f}%")
        else:
            print(f"🎯 Success Rate: No reviews yet")
        
        print(f"\n📦 Slot Distribution:")
        slot_names = {
            1: "Slot 1 (Every day)",
            2: "Slot 2 (Every 3 days)", 
            3: "Slot 3 (Every 7 days)",
            4: "Slot 4 (Every 14 days)",
            5: "Slot 5 (Every 30 days)",
            6: "Slot 6 (Learned!)"
        }
        
        for slot_num, count in slot_distribution:
            slot_name = slot_names.get(slot_num, f"Slot {slot_num}")
            print(f" {slot_name}: {count} cards")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error fetching statistics: {e}")
        time.sleep(2)
    finally:
        if conn:
            conn.close()
    clear_screen()

def logout():
    """Secure logout from system."""
    global current_user_id, current_box_id
    
    try:
        if current_user_id:
            conn = get_connection()
            cur = conn.cursor()
            
            
            cur.execute("SELECT username FROM users WHERE id = %s", (current_user_id,))
            user_result = cur.fetchone()
            
            if user_result:
                username = user_result[0]
                print(f"\n🎯 User: {username}")
                print("✅ Your changes have been saved.")
                print("👋 See you again soon...")
            else:
                print("✅ Logged out successfully!")
            
            cur.close()
            conn.close()
        else:
            print("❌ No users are currently logged in!")
        
        
        current_user_id = None
        current_box_id = None
        
        
        time.sleep(2)
        
    except Exception as e:
        print(f"⚠️ Error logging out: {e}")
        current_user_id = None
        current_box_id = None
    
    clear_screen()
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
        print("5. Show Statistics")
        print("6. Logout")

        
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
            show_statistics()
        elif choice == "6":
            logout()
        else:
            print("❌ Invalid choice!")


if __name__ == "__main__":
    clear_screen()
    print("🎯 Welcome to Leitner Box System!")
    time.sleep(1)
    clear_screen()
    menu()
