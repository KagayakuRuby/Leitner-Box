import psycopg2
from datetime import datetime

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

#==================== Login Panel ===============
def register():
    while True:
        username = input("Please enter your username to register: ")
        password = input("Please enter your password: ")
        confirm_password = input("Please confirm your password: ")

        if password != confirm_password:
            print("Passwords do not match! Try again.")
            continue 
        break

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users(username, password_hash) VALUES(%s, %s);",
                    (username, password))
        conn.commit()
        print("User registered successfully!")
    except Exception as e:
        print(f"User registration failed! Error: {e}")
    finally:
        if conn:
            conn.close()

        
def login():
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

def reviewcard():
    pass

def logout():
    pass

    
# ====================== UI ======================
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
