import psycopg2
from datetime import datetime , timedelta
import hashlib
import os

import time


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
        conn = get_connection()
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
            cur = self.db.conn.cursor()
            cur.execute(
                "INSERT INTO categories (user_id, name) VALUES (%s, %s)",
                (self.current_user, name)
            )
            self.db.conn.commit()
            cur.close()
            print(" Category created successfully! ✅")
        except Exception as e:
            print(f" Error creating category ❌: {e}")


def show_categories(self):
        try:
            cur = self.db.conn.cursor()
            cur.execute(
                "SELECT id, name FROM categories WHERE user_id = %s ORDER BY name",
                (self.current_user,)
            )
            categories = cur.fetchall()
            cur.close()
            
            if categories:
                print("\n📂 Your Categories:")
                for cat_id, name in categories:
                    print(f" {cat_id}. {name}")
            else:
                print(" You haven't created any categories yet! 📝")
            return categories
        except Exception as e:
            print(f" Error displaying categories ❌: {e}")
            return []

def change_card_category(self, card_id):
        """Change card category"""
        try:
            # Show available categories
            categories = self.show_categories()
            if not categories:
                print(" Please create a category first! ❌")
                return
            
            print("\n🎯 Select new category:")
            for cat_id, name in categories:
                print(f" {cat_id}. {name}")
            
            new_cat_id = int(input("New category ID 📑: "))
            
            cur = self.db.conn.cursor()
            cur.execute(
                "UPDATE cards SET category_id = %s WHERE id = %s",
                (new_cat_id, card_id)
            )
            
            self.db.conn.commit()
            cur.close()
            print(" Card category changed! ✅")
            
        except ValueError:
            print(" Category ID must be a number ❌")
        except Exception as e:
            print(f" Error changing category ❌ : {e}")


def addcard():
    pass

def show_user_cards(self):
        """show all user cards."""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                """SELECT c.id, c.question, c.answer, c.box, c.next_review, c.is_important, cat.name as category_name 
                FROM cards c 
                JOIN categories cat ON c.category_id = cat.id 
                WHERE c.user_id = ? 
                ORDER BY c.is_important DESC, c.box, c.next_review""",
                (self.current_user,)
            )
            cards = cursor.fetchall()
            cursor.close()
            
            return cards
        except Exception as e:
            print(f" Error fetching cards ❌: {e}")
            return []

def modifycard(self,card_id,current_user):
        """card edit menu."""
        try:
        # creating direct connectin from the cursor
            conn = get_connection()
            cur = conn.cursor()
        
            cur.execute(
                "SELECT id FROM cards WHERE id = %s AND user_id = %s",
                (card_id, current_user)
                )   
            card_exists = cur.fetchone()
        
            if not card_exists:
                print("✗ Card not found or you don't have permission")
                return
        
            cur.close() #close cursor
            return card_exists
        
        except Exception as e:
            print(f"Error: {e}")

        self.clear_screen()
        print("\n" + "="*50)
        print(" 🔧 MODIFY CARD")
        print("="*50)
        
        cards = self.show_user_cards()
        if not cards:
            print(" You don't have any cards to modify! ❌")
            time.sleep(2)
            return
        
        print("\nYour cards:")
        for card in cards:
            important_flag = " ⭐" if card['is_important'] else ""
            print(f" {card['id']}. {card['question'][:30]}... (Box {card['box']}){important_flag}")
        
        try:
            card_id = int(input("\nEnter card ID to modify: "))
            
            # checking card existence and ownership
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT id FROM cards WHERE id = ? AND user_id = ?",
                (card_id, self.current_user)
            )
            card_exists = cursor.fetchone()
            
            if not card_exists:
                print(" Card not found or you don't have permission to modify it! ❌")
                time.sleep(2)
                return
            
            # display current card information
            cursor.execute(
                """SELECT c.question, c.answer, c.box, c.is_important, cat.name as category_name 
                FROM cards c 
                JOIN categories cat ON c.category_id = cat.id 
                WHERE c.id = ?""",
                (card_id,)
            )
            card_details = cursor.fetchone()
            
            print(f"\n📝 Editing Card #{card_id}")
            print(f"Current Question: {card_details['question']}")
            print(f"Current Answer: {card_details['answer']}")
            print(f"Current Box: {card_details['box']}")
            print(f"Important: {'Yes ⭐' if card_details['is_important'] else 'No'}")
            print(f"Category: {card_details['category_name']}")
            
            # receive changes
            print("\nWhat would you like to modify? 🤔")
            print("1. 📝 Edit Question")
            print("2. ✅ Edit Answer") 
            print("3. 🏠 Change Box")
            print("4. ⭐ Toggle Importance")
            print("5. 📁 Change Category")
            print("6. 🔙 Cancel")
            
            choice = input("\nChoose an option: ").strip()
            
            if choice == "1":
                new_question = input("New question: ").strip()
                if new_question:
                    cursor.execute(
                        "UPDATE cards SET question = ? WHERE id = ?",
                        (new_question, card_id)
                    )
                    print("✅ Question updated successfully!")
            
            elif choice == "2":
                new_answer = input("New answer: ").strip()
                if new_answer:
                    cursor.execute(
                        "UPDATE cards SET answer = ? WHERE id = ?",
                        (new_answer, card_id)
                    )
                    print("✅ Answer updated successfully!")
            
            elif choice == "3":
                print("\nSelect new box:")
                print("1: New (Review daily)")
                print("2: Familiar (Review every 3 days)")
                print("3: Intermediate (Review every 7 days)")
                print("4: Good (Review every 14 days)")
                print("5: Almost Mastered (Review every 30 days)")
                print("6: Mastered (No review needed)")
                
                new_box = int(input("New box (1-6): "))
                if 1 <= new_box <= 6:
                    intervals = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30, 6: 999}
                    next_review = datetime.now() + timedelta(days=intervals[new_box])
                    
                    cursor.execute(
                        "UPDATE cards SET box = ?, next_review = ? WHERE id = ?",
                        (new_box, next_review.strftime('%Y-%m-%d'), card_id)
                    )
                    print(f"✅ Card moved to Box  {new_box}!")
                else:
                    print(" Box must be between 1 and 6! ❌")
            
            elif choice == "4":
                cursor.execute("SELECT is_important FROM cards WHERE id = ?", (card_id,))
                current_status = cursor.fetchone()['is_important']
                new_status = not current_status
                
                cursor.execute(
                    "UPDATE cards SET is_important = ? WHERE id = ?",
                    (1 if new_status else 0, card_id)
                )
                action = "marked as important ⭐" if new_status else "unmarked"
                print(f"✅ Card {action}!")
            
            elif choice == "5":
                categories = self.show_categories()
                if categories:
                    print("\nAvailable categories:")
                    for category in categories:
                        print(f" {category['id']}. {category['name']}")
                    
                    new_category_id = int(input("New category ID: "))
                    cursor.execute(
                        "UPDATE cards SET category_id = ? WHERE id = ?",
                        (new_category_id, card_id)
                    )
                    print(" Category changed successfully! ✅")
                else:
                    print(" No categories available! ❌")
            
            elif choice == "6":
                print(" Modification cancelled. ❌")
            else:
                print(" Invalid option! ❌")
            
            self.db.conn.commit()
            cursor.close()
            time.sleep(2)
            
        except ValueError:
            print(" Please enter a valid card ID! ❌")
            time.sleep(2)
        except Exception as e:
            print(f" Error modifying card ❌: {e}")
            time.sleep(2)


def delete_card(self):
        """delete card."""
        self.clear_screen()
        print("\n" + "="*50)
        print(" 🗑️ DELETE CARD")
        print("="*50)
        
        cards = self.show_user_cards()
        if not cards:
            print(" You don't have any cards to delete! ❌")
            time.sleep(2)
            return
        
        print("\nYour cards:")
        for card in cards:
            important_flag = " ⭐" if card['is_important'] else ""
            print(f" {card['id']}. {card['question'][:30]}... (Box {card['box']}){important_flag}")
        
        try:
            card_id = int(input("\nEnter card ID to delete: "))
            
            # checking card existence and ownership
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT id, question FROM cards WHERE id = ? AND user_id = ?",
                (card_id, self.current_user)
            )
            card_details = cursor.fetchone()
            
            if not card_details:
                print(" Card not found or you don't have permission to delete it! ❌")
                time.sleep(2)
                return
            
            print(f"\n⚠️ You are about to delete this card:")
            print(f"Question: {card_details['question']}")
            
            confirm = input("\nAre you sure you want to delete this card? This action cannot be undone! (y/n): ").lower().strip()
            
            if confirm == 'y':
                # delete relevant browsinng history
                cursor.execute("DELETE FROM reviews WHERE card_id = ?", (card_id,))
                # delete card
                cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
                self.db.conn.commit()
                cursor.close()
                print(" Card deleted successfully! ✅")
            else:
                print(" Deletion cancelled. ❌")
            
            time.sleep(2)
            
        except ValueError:
            print(" Please enter a valid card ID! ❌")
            time.sleep(2)
        except Exception as e:
            print(f" Error deleting card ❌: {e}")
            time.sleep(2)  
              
def update_card(self, card_id, correct):
        """Card progress update based on Leitner algorithm"""
        try:
            cur = self.db.conn.cursor()
            
            # Get current box
            cur.execute("SELECT box FROM cards WHERE id = %s", (card_id,))
            current_box = cur.fetchone()[0]
            
            # Calculate new box
            if correct:
                new_box = min(current_box + 1, 6)
            else:
                new_box = max(1, current_box - 1)
            
            # Calculate next review date
            intervals = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30, 6: 999}
            next_review = datetime.now() + timedelta(days=intervals[new_box])
            
            # Update card
            cur.execute(
                "UPDATE cards SET box = %s, next_review = %s WHERE id = %s",
                (new_box, next_review, card_id)
            )
            
            # Save review history
            cur.execute(
                "INSERT INTO reviews (user_id, card_id, correct) VALUES (%s, %s, %s)",
                (self.current_user, card_id, correct)
            )
            
            self.db.conn.commit()
            cur.close()
            
            box_names = {
                1: "Box 1 (New - Daily review)",
                2: "Box 2 (Familiar - Every 3 days)", 
                3: "Box 3 (Intermediate - Every 7 days)",
                4: "Box 4 (Good - Every 14 days)",
                5: "Box 5 (Almost Mastered - Every 30 days)", 
                6: "Box 6 (Learned - No review needed)"
            }
            
            if correct:
                print(f"🎯 Excellent! Moved to {box_names[new_box]}")
            else:
                print(f"🔄 Returned to {box_names[new_box]}")
                
        except Exception as e:
            print(f" Error updating card ❌ : {e}")


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
            cur = self.db.conn.cursor()
            
            # Get current status
            cur.execute("SELECT is_important FROM cards WHERE id = %s", (card_id,))
            current_status = cur.fetchone()[0]
            
            # Toggle status
            new_status = not current_status
            cur.execute(
                "UPDATE cards SET is_important = %s WHERE id = %s",
                (new_status, card_id)
            )
            
            self.db.conn.commit()
            cur.close()
            
            action = "marked as important ⭐" if new_status else "unmarked"
            print(f"✅ Card {action}")
            
        except Exception as e:
            print(f" Error toggling importance ❌: {e}")
    
    

# ==================== REVIEW METHODS ====================


def reviewcard():
    pass


# ==================== STATISTICS METHODS ====================
    
def show_statistics(self):
        """show user statistics"""
        self.clear_screen()
        print("\n" + "="*50)
        print(" 📊 YOUR STATISTICS")
        print("="*50)
        
        try:
            cursor = self.db.conn.cursor()
            
            # basic statistics
            cursor.execute("SELECT COUNT(*) FROM cards WHERE user_id = ?", (self.current_user,))
            total_cards = cursor.fetchone()[0]
            
            cursor.execute(
                "SELECT COUNT(*) FROM cards WHERE user_id = ? AND date(next_review) <= date('now')",
                (self.current_user,)
            )
            due_cards = cursor.fetchone()[0]
            
            cursor.execute(
                "SELECT COUNT(*) FROM cards WHERE user_id = ? AND is_important = 1",
                (self.current_user,)
            )
            important_cards = cursor.fetchone()[0]
            
            # distributing cards into boxes
            cursor.execute(
                """SELECT box, COUNT(*) as count 
                FROM cards WHERE user_id = ? 
                GROUP BY box ORDER BY box""",
                (self.current_user,)
            )
            box_distribution = cursor.fetchall()
            
            # browsing statistics
            cursor.execute(
                """SELECT 
                    COUNT(*) as total_reviews,
                    SUM(CASE WHEN correct THEN 1 ELSE 0 END) as correct_reviews
                FROM reviews WHERE user_id = ?""",
                (self.current_user,)
            )
            review_stats = cursor.fetchone()
            
            cursor.close()
            
            # show statistics
            print(f"\n📈 Basic Statistics:")
            print(f"📜 Total Cards: {total_cards}")
            print(f"📚 Due for Review: {due_cards}")
            print(f"⭐ Important Cards: {important_cards}")
            
            if review_stats['total_reviews'] > 0:
                success_rate = (review_stats['correct_reviews'] / review_stats['total_reviews']) * 100
                print(f" Success Rate: {success_rate:.1f}%")
            
            print(f"\n🎯 Box Distribution:")
            box_names = {1: "New", 2: "Familiar", 3: "Intermediate", 4: "Good", 5: "Almost Mastered", 6: "Mastered"}
            for dist in box_distribution:
                box_name = box_names.get(dist['box'], f"Box {dist['box']}")
                print(f" {box_name}: {dist['count']} cards")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f" Error fetching statistics ❌ : {e}")
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
