import psycopg
from dotenv import load_dotenv
from random import randint
import os

load_dotenv()

def get_connection():
    return psycopg.connect(os.environ.get("DB_URL"))

#CREATE THE TABLE
def create_users_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS users (
    User_id BIGINT PRIMARY KEY,
    First_Name TEXT,
    Username_Name TEXT,
    Temporary_Account BOOLEAN DEFAULT FALSE,
    Banned BOOLEAN DEFAULT FALSE,
    Expiry_Date TEXT DEFAULT 'N/A',
    Last_Call TEXT DEFAULT 'N/A',
    In_Call BOOLEAN DEFAULT FALSE,
    Err_Num INTEGER,
    Voice TEXT DEFAULT 'Jorch',
    Accent TEXT DEFAULT 'North America',
    In_Action text DEFAULT 'NN',
    Custom_Script TEXT DEFAULT 'N/A',
    First_Call TEXT DEFAULT 'N/A'
);
            """)
            conn.commit()

allowed_columns = {"User_id", "First_Name","Banned", "Expiry_Date","Temporary_Account",'In_Call','Last_Call','Username_Name', 'Err_Num','Voice','Accent','In_Action','Custom_Script','First_Call'}

#GET A USER INFO 
def get_user_info(user_id, col):
    
    if col not in allowed_columns:
        raise ValueError("Invalid column name")
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = f"SELECT {col} FROM users WHERE User_id = %s"
            cur.execute(query, (user_id,))
            result = cur.fetchone()
            return result[0] if result else None

def reset_all_user_actions():
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = "UPDATE users SET In_Action = %s"
            cur.execute(query, ('NN',))
        conn.commit()

#ADD A USER TO THE DATABASE
def add_user(user):
    err = randint(0,2)
    if user.username:
        username = "@"+user.username
    else:
        username='None'
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (User_id, First_Name, Username_Name, Err_Num)
                VALUES (%s, %s, %s,%s)
                ON CONFLICT (User_id) DO NOTHING
            """, (user.id,user.first_name, username, err))
            conn.commit()

#SET USER VALUE
def set_user_value(user_id, col, value):
    if col not in allowed_columns:
        raise ValueError("Invalid column name")
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = f"UPDATE users SET {col} = %s WHERE User_id = %s"
            cur.execute(query, (value, user_id))
        conn.commit()

#COUNT USERS
def get_user_count():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users")
            count = cur.fetchone()[0]
            return count
        
#CHECK IF USER IN THE DATABASE
def user_exists(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE User_id = %s", (user_id,))
            return cur.fetchone() is not None
        