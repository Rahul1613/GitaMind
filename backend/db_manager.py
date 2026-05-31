import sqlite3
import bcrypt
import os
import uuid
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Create Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    ''')
    # Create Chats table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            title TEXT,
            created_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    # Create Messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT,
            role TEXT,
            content TEXT,
            docs TEXT,
            created_at DATETIME,
            FOREIGN KEY (chat_id) REFERENCES chats (id)
        )
    ''')
    conn.commit()
    conn.close()

# -----------------
# User Management
# -----------------
def create_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False, "Username already exists"
    
    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    c.execute("INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)", 
              (user_id, username, password_hash))
    conn.commit()
    conn.close()
    return True, user_id

def verify_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    
    if row:
        user_id, password_hash = row
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return True, user_id
    return False, "Invalid username or password"

# -----------------
# Chat Management
# -----------------
def create_chat(user_id, title):
    conn = get_connection()
    c = conn.cursor()
    chat_id = str(uuid.uuid4())
    created_at = datetime.now()
    c.execute("INSERT INTO chats (id, user_id, title, created_at) VALUES (?, ?, ?, ?)", 
              (chat_id, user_id, title, created_at))
    conn.commit()
    conn.close()
    return chat_id

def get_user_chats(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, title, created_at FROM chats WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": row[0], "title": row[1], "created_at": row[2]} for row in rows]

# -----------------
# Message Management
# -----------------
def add_message(chat_id, role, content, docs=None):
    conn = get_connection()
    c = conn.cursor()
    message_id = str(uuid.uuid4())
    created_at = datetime.now()
    docs_json = json.dumps(docs) if docs else None
    
    c.execute("INSERT INTO messages (id, chat_id, role, content, docs, created_at) VALUES (?, ?, ?, ?, ?, ?)", 
              (message_id, chat_id, role, content, docs_json, created_at))
    conn.commit()
    conn.close()
    return message_id

def get_chat_messages(chat_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT role, content, docs FROM messages WHERE chat_id = ? ORDER BY created_at ASC", (chat_id,))
    rows = c.fetchall()
    conn.close()
    
    messages = []
    for row in rows:
        messages.append({
            "role": row[0],
            "content": row[1],
            "docs": json.loads(row[2]) if row[2] else None
        })
    return messages

# Initialize db when this module is imported
init_db()
