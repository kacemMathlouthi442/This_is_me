from UsersDB import set_user_value, get_user_info
from datetime import datetime, timedelta
from Functions import duration
import random, string, os, psycopg
from dotenv import load_dotenv

load_dotenv()
def get_connection():
    return psycopg.connect(os.environ.get("DB_URL"))

#CREATE THE TABLE
def create_keys_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS Keys (
    Key TEXT PRIMARY KEY,
    Used BOOLEAN DEFAULT FALSE
);
            """)
            conn.commit()


types = {'2HOUR','1DAYZ','3DAYZ','1WEEK','1MNTH'}

def show_valid_keys(key_type):
    if key_type not in types:
        return '❌ Invalid key type.'
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = "SELECT Key FROM keys WHERE key LIKE %s AND Used = FALSE;"
            cur.execute(query, (f"%{key_type}%",))  # correctly uses key_type
            keys = [f"`{row[0]}`" for row in cur.fetchall()]
            return keys if keys else ["⚠️ No available keys."]



def reset_key(key_type): 
    if key_type not in types:
        return '❌ Invalid key type.'
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = "UPDATE Keys SET Used = FALSE WHERE Used = TRUE AND Key LIKE %s"
            cur.execute(query, (f"%-{key_type}-%",))
        conn.commit()
    
    return '✅ Keys have been reset successfully.'


#SET USER VALUE
def update_key(Key, value):
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = f"UPDATE Keys SET Used = %s WHERE Key = %s"
            cur.execute(query, (value, Key))
        conn.commit()
       

# Duration logic mapping: base_time, bonus_time, display label
DURATION_MAP = {
    '2HOUR': (timedelta(hours=2), timedelta(hours=1), '2Hours\+\(1Hour Free\)'),
    '1DAYZ': (timedelta(days=1), timedelta(hours=12), '1Day\+\(12Hours Free\)'),
    '3DAYZ': (timedelta(days=3), timedelta(days=1), '3Days\+\(1Day Free\)'),
    '1WEEK': (timedelta(days=7), timedelta(days=3), '1Week\+\(3Days Free\)'),
    '1MNTH': (timedelta(days=30), timedelta(days=10), '1Month\+\(10Days Free\)'),
}

def redeem_keys(user_id, key):
    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Check if key exists and is unused
            cur.execute("SELECT Used FROM Keys WHERE Key = %s", (key,))
            result = cur.fetchone()

            if not result:
                return '❌ Unavailable Key\!'
            if result[0]:  # Key already used
                return '❌ Expired Key\!'

            # 2. Extract duration code (2nd segment of the key)
            parts = key.split("-")
            if len(parts) != 5:
                return '❌ Invalid Key Format\!'

            duration_code = parts[1]


            base_time, bonus_time, label = DURATION_MAP[duration_code]

            # 3. Get current expiry
            expiry_str = get_user_info(user_id, 'Expiry_Date')
            now = datetime.now()

            # User has no active time
            is_new = expiry_str == 'N/A' or datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S.%f") < now
            current_expiry = now if is_new else datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S.%f")

            # 4. Calculate new expiry and update
            added_time = base_time + bonus_time if is_new else base_time
            new_expiry = current_expiry + added_time

            set_user_value(user_id, 'Expiry_Date', str(new_expiry))
            update_key(key, True)

            # 5. Build message
            if is_new:
                msg = fr'*✅ {label} *Key Redeemed Successfully\!\nYour subscription has been updated\, Thank you for choosing *AORUS OTP*\.'
            else:
                duration_text = duration(duration_code)
                msg = fr'*✅ {duration_text} *Key Redeemed Successfully\!\nYour subscription has been updated\, Thank you for choosing *AORUS OTP*\.'
            return msg

def random_segment(length=5):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_key(duration_code):
    return f"AORUS-{duration_code}-{random_segment()}-{random_segment()}-{random_segment()}"

def generate_and_add_keys():
    durations = ['2HOUR', '1DAYZ', '3DAYZ', '1WEEK', '1MNTH']
    total_per_duration = 30

    with get_connection() as conn:
        with conn.cursor() as cur:
            count_added = 0
            for duration in durations:
                keys_added = 0
                while keys_added < total_per_duration:
                    key = generate_key(duration)
                    try:
                        cur.execute("INSERT INTO Keys (Key, Used) VALUES (%s, FALSE)", (key,))
                        keys_added += 1
                        count_added += 1
                    except psycopg.errors.UniqueViolation:
                        # Key already exists, just skip and generate another
                        conn.rollback()
                    else:
                        conn.commit()
            print(f"Added {count_added} keys total (30 per duration).")