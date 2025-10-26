import psycopg2
from datetime import datetime , timedelta
import hashlib
import os
import time


def connect_db():
    """
    Establish connection to PostgreSQL database
    """
    return psycopg2.connect(
        host="localhost", # Database server address
        database="leitnerbox", # Database name
        user="postgres", # Database username
        password="postgres" # Database password
    )

def search_cards(user_id, search_text=None):
    """
    Search through a user's cards
    
    Parameters:
        user_id (int): User ID

    Returns:
        list: List of found cards
    """
    # Establish database connection
    conn = connect_db()
    cur = conn.cursor()
    
    # Call the search function in database
    cur.callproc('search_cards', (user_id, search_text))
    
    # Get results
    results = cur.fetchall()
    
    # Close connection
    cur.close()
    conn.close()
    
    return results

#==================== Login Panel =============== # Ruby
def register():
    conn = connect_db()
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
        password = input("Please enter your password 😊 : ")
        confirm_password = input("Please confirm your password 🫣: ")

        if password != confirm_password:
            print("Passwords do not match! Try again.😕")
            continue
        else:
            break

    try:
        cur.execute(
            "INSERT INTO users(username, password_hash) VALUES(%s, %s);",
            (username, password)
        )
        conn.commit()
        print("User registered successfully! 🤗🎉")
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
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")

    conn = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password_hash=%s LIMIT 1;", (username, password))
        user = cur.fetchone()
        if user:
            print(f"✅ Welcome back, {username}!")
            dashbord()
        else:
            print(" Username or password is invalid! ❌")
    except Exception as e:
        print("Username or Password is invalid! 🙅")
    finally:
        if conn:conn.close()


def hash_password(self, password):
        """password hashing."""
        return hashlib.sha256(password.encode()).hexdigest()
    
def clear_screen(self):
        """clear screen."""
        os.system('cls' if os.name == 'nt' else 'clear')


# ==================== CARD MANAGEMENT METHODS ====================

def showbox():
    pass


def create_category(self):
    print("\n--- 📁 Create New Category ---")
    name = input("Category name: ")
    
    if not name:
        print(" Category name cannot be empty ❌")
        return
    
    try:
        cursor = self.db.conn.cursor()
        cursor.execute("INSERT INTO categories (user_id, name) VALUES (%s, %s)", (self.current_user, name))
        self.db.conn.commit()
        cursor.close()
        print(" Category created successfully! ✅")
    except Exception as e:
        print(f"❌ Error creating category : {e}")



def show_categories(self):
    """Show user's categories"""
    try:
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id, name FROM categories WHERE user_id = %s ORDER BY name", (self.current_user,))
        categories = cursor.fetchall()
        cursor.close()
        
        if categories:
            print("\n📂 Your Categories:")
            for cat_id, name in categories:
                print(f" {cat_id}. {name}")
        else:
            print("📝 You haven't created any categories yet!")
        
        return categories
        
    except Exception as e:
        print(f"❌ Error displaying categories: {e}")
        return []


def change_card_category(self, card_id):
    """Change card category"""
    try:
        categories = self.show_categories()
        if not categories:
            print(" Please create a category first! ❌")
            return
        
        print("\n🎯 Select new category:")
        for cat_id, name in categories:
            print(f" {cat_id}. {name}")
        
        new_cat_id = int(input("New category ID 📑: "))
        
        cursor = self.db.conn.cursor()
        cursor.execute("UPDATE cards SET category_id = %s WHERE id = %s", (new_cat_id, card_id))
        self.db.conn.commit()
        cursor.close()
        
        print(" Card category changed! ✅")
        
    except ValueError:
        print(" Category ID must be a number ❌")
    except Exception as e:
        print(f"❌ Error changing category: {e}")


def addcard():
    pass


def show_user_cards(self):
    """Show all user cards"""
    try:
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT c.id, c.question, c.answer, c.box, c.next_review, c.is_important, cat.name 
            FROM cards c 
            JOIN categories cat ON c.category_id = cat.id 
            WHERE c.user_id = %s 
            ORDER BY c.is_important DESC, c.box, c.next_review
        """, (self.current_user,))
        
        cards = cursor.fetchall()
        cursor.close()
        return cards
        
    except Exception as e:
        print(f"❌ Error fetching cards: {e}")
        return []


def modifycard(self, card_id):
    """Edit card menu"""
    self.clear_screen()
    print("\n" + "="*50)
    print(" 🔧 MODIFY CARD")
    print("="*50)
    
    # Check if card exists and belongs to user
    try:
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT c.question, c.answer, c.box, c.is_important, cat.name as category_name FROM cards c JOIN categories cat ON c.category_id = cat.id WHERE c.id = %s AND c.user_id = %s",
            (card_id, self.current_user)
        )
        card = cursor.fetchone()
        
        if not card:
            print(" Card not found or access denied! ❌")
            time.sleep(2)
            return
        
        # Show current card info
        print(f"\n📝 Editing Card #{card_id}")
        print(f"Question: {card[0]}")
        print(f"Answer: {card[1]}")
        print(f"Box: {card[2]}")
        print(f"Important: {'Yes ⭐' if card[3] else 'No'}")
        print(f"Category: {card[4]}")
        
        # Show modification options
        print("\nWhat would you like to change?")
        print("1. 📝 Edit Question")
        print("2. ✅ Edit Answer")
        print("3. 🏠 Change Box")
        print("4. ⭐ Toggle Importance")
        print("5. 📁 Change Category")
        print("6. 🔙 Cancel")
        
        choice = input("\nChoose option: ")
        
        if choice == "1":
            new_question = input("New question: ")
            if new_question:
                cursor.execute("UPDATE cards SET question = %s WHERE id = %s", (new_question, card_id))
                print(" Question updated! ✅")
        
        elif choice == "2":
            new_answer = input("New answer: ")
            if new_answer:
                cursor.execute("UPDATE cards SET answer = %s WHERE id = %s", (new_answer, card_id))
                print(" Answer updated! ✅")
        
        elif choice == "3":
            print("\nSelect box:")
            boxes = ["New (Daily)", "Familiar (3 days)", "Intermediate (7 days)", "Good (14 days)", "Almost Mastered (30 days)", "Mastered"]
            for i, box in enumerate(boxes, 1):
                print(f"{i}. {box}")
            
            new_box = int(input("Box number (1-6): "))
            if 1 <= new_box <= 6:
                intervals = [1, 3, 7, 14, 30, 999]
                next_review = datetime.now() + timedelta(days=intervals[new_box-1])
                cursor.execute("UPDATE cards SET box = %s, next_review = %s WHERE id = %s", (new_box, next_review, card_id))
                print(f"✅ Moved to Box {new_box}!")
            else:
                print(" Box must be 1-6! ❌")
        
        elif choice == "4":
            new_status = not card[3]
            cursor.execute("UPDATE cards SET is_important = %s WHERE id = %s", (new_status, card_id))
            status_text = "marked as important ⭐" if new_status else "unmarked"
            print(f"✅ Card {status_text}!")
        
        elif choice == "5":
            categories = self.show_categories()
            if categories:
                new_cat_id = int(input("New category ID: "))
                cursor.execute("UPDATE cards SET category_id = %s WHERE id = %s", (new_cat_id, card_id))
                print(" Category changed! ✅")
            else:
                print(" No categories available! ❌")
        
        elif choice == "6":
            print(" Changes cancelled. ℹ️")
        else:
            print(" Invalid option! ❌")
        
        self.db.conn.commit()
        cursor.close()
        time.sleep(2)
        
    except ValueError:
        print(" Please enter a valid number! ❌")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(2)


def delete_card(self):
    """Delete  card."""
    self.clear_screen()
    print("\n" + "="*50)
    print(" 🗑️ DELETE CARD")
    print("="*50)
    
    cards = self.show_user_cards()
    if not cards:
        print(" No cards to delete! ❌")
        time.sleep(2)
        return
    
    print("\nYour cards:")
    for card in cards:
        star = " ⭐" if card['is_important'] else ""
        preview = card['question'][:30] + "..." if len(card['question']) > 30 else card['question']
        print(f" {card['id']}. {preview} (Box {card['box']}){star}")
    
    try:
        card_id = int(input("\nEnter card ID to delete: "))
        
        with self.db.conn.cursor() as cursor:
            # Check if card exists and belongs to user
            cursor.execute(
                "SELECT question FROM cards WHERE id = %s AND user_id = %s", 
                (card_id, self.current_user)
            )
            card = cursor.fetchone()
            
            if not card:
                print(" Card not found! ❌")
                time.sleep(2)
                return
            
            print(f"\n📋 Question: {card[0]}")
            confirm = input("\n❓ Confirm deletion? (y/n): ").lower()
            
            if confirm == 'y':
                cursor.execute("DELETE FROM reviews WHERE card_id = %s", (card_id,))
                cursor.execute("DELETE FROM cards WHERE id = %s", (card_id,))
                self.db.conn.commit()
                print("✅ Card deleted!")
            else:
                print(" Deletion cancelled. ℹ️")
        
        time.sleep(2)
        
    except ValueError:
        print(" Please enter a valid number! ❌")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(2)


def update_card(self, card_id, correct):
    """Card progress update based on Leitner algorithm"""
    try:
        cursor = self.db.conn.cursor()
        
        # Get current box
        cursor.execute("SELECT box FROM cards WHERE id = %s", (card_id,))
        current_box = cursor.fetchone()[0]
        
        # Calculate new box
        if correct:
            new_box = current_box + 1 if current_box < 6 else 6
        else:
            new_box = current_box - 1 if current_box > 1 else 1
        
        # Set next review date
        review_days = [1, 3, 7, 14, 30, 999]
        next_review = datetime.now() + timedelta(days=review_days[new_box-1])
        
        # Update card and save review
        cursor.execute("UPDATE cards SET box = %s, next_review = %s WHERE id = %s", 
                      (new_box, next_review, card_id))
        cursor.execute("INSERT INTO reviews (user_id, card_id, correct) VALUES (%s, %s, %s)", 
                      (self.current_user, card_id, correct))
        
        self.db.conn.commit()
        cursor.close()
        
        # Show result
        box_names = ["New", "Familiar", "Intermediate", "Good", "Almost Mastered", "Mastered"]
        if correct:
            print(f"✅ Advanced to Box {new_box} ({box_names[new_box-1]})")
        else:
            print(f"🔄 Back to Box {new_box} ({box_names[new_box-1]})")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def validate_card_ownership(self, card_id):
        """Verify that card belongs to current user"""
        try:
            cur = self.db.conn.cursor()
            cur.execute(
                "SELECT id FROM cards WHERE id = %s AND user_id = %s",
                (card_id, self.current_user)
            )
            result = cur.fetchone()
            cur.close()
            return result is not None
        except Exception as e:
            print(f" Ownership verification error ❌: {e}")
            return False
        

def toggle_important(self, card_id):
    """Mark/unmark card as important"""
    try:
        cursor = self.db.conn.cursor()
        
        # Get current important status
        cursor.execute("SELECT is_important FROM cards WHERE id = %s", (card_id,))
        current = cursor.fetchone()[0]
        
        # Switch to opposite status
        new_status = not current
        cursor.execute("UPDATE cards SET is_important = %s WHERE id = %s", (new_status, card_id))
        
        self.db.conn.commit()
        cursor.close()
        
        # Show result
        if new_status:
            print("✅ Card marked as important ⭐")
        else:
            print(" Card unmarked ✅")
            
    except Exception as e:
        print(f"❌ Error: {e}")


# ==================== REVIEW METHODS ====================

def reviewcard():
    pass

# ==================== STATISTICS METHODS ====================

def show_statistics(self):
    """Show user statistics"""
    self.clear_screen()
    print("\n" + "="*50)
    print(" 📊 YOUR STATISTICS")
    print("="*50)
    
    try:
        cursor = self.db.conn.cursor()
        
        # Get all statistics in one go
        cursor.execute("SELECT COUNT(*) FROM cards WHERE user_id = %s", (self.current_user,))
        total_cards = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cards WHERE user_id = %s AND next_review <= CURRENT_DATE", (self.current_user,))
        due_cards = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cards WHERE user_id = %s AND is_important = TRUE", (self.current_user,))
        important_cards = cursor.fetchone()[0]
        
        cursor.execute("SELECT box, COUNT(*) FROM cards WHERE user_id = %s GROUP BY box ORDER BY box", (self.current_user,))
        box_distribution = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*), SUM(CASE WHEN correct THEN 1 ELSE 0 END) FROM reviews WHERE user_id = %s", (self.current_user,))
        total_reviews, correct_reviews = cursor.fetchone()
        
        cursor.close()
        
        # Display statistics
        print(f"\n📈 Basic Statistics:")
        print(f"📜 Total Cards: {total_cards}")
        print(f"📚 Due for Review: {due_cards}")
        print(f"⭐ Important Cards: {important_cards}")
        
        if total_reviews > 0:
            success_rate = (correct_reviews / total_reviews) * 100
            print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print(f"\n📦 Box Distribution:")
        box_names = ["New", "Familiar", "Intermediate", "Good", "Almost Mastered", "Mastered"]
        for box_num, count in box_distribution:
            box_name = box_names[box_num-1] if 1 <= box_num <= 6 else f"Box {box_num}"
            print(f" {box_name}: {count} cards")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error fetching statistics: {e}")
        time.sleep(2)


def logout(self):
    """Secure logout from system."""
    try:
        if self.current_user:
            # getting the username before log out.
            cur = self.db.conn.cursor()
            cur.execute("SELECT username FROM users WHERE id = %s", (self.current_user,))
            username = cur.fetchone()[0]
            cur.close()
            
            print(f"\n 🎯 usre : {username}")
            print(" Your changes have been saved. ✅ ")
            print(" See you again soon 👋...")
            
            self.current_user = None
        else:
            print(" no users are currently logged in! ❌")
        
        # slight delay in displaying the message.
        import time
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f" error logging out!⚠️ : {e}")
        self.current_user = None
        return True


# ====================== UI ====================== #Ruby
def menu():
     while True:
        print("\n--- 📋 Welcom To Login Pannel 🎊 ---")
        print("1.🔐 Register")
        print("2.🔑 Login")
        print("3.🚪 Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Have Good Time ☺️💓:)")
            time.sleep(1.0)
            exit()
        else:
            print(" Invalid choice! ❌")

def dashbord():
    while True:
        print("\n--- 📋 Welcom To Dashbord Pannel ---")
        print("1.📊 Show Box")
        print("2.📝 Add Card")
        print("3.🔧 Modify Card")
        print("4.📚 Review Card")
        print("5.🔓 Logout")

        
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
            print(" Invalid choice! ❌")


if __name__ == "__main__":
    menu()
