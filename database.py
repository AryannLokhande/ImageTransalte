# database.py
import sqlite3

def init_db():
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            extracted_text TEXT,
            english TEXT,
            hindi TEXT,
            german TEXT,
            spanish TEXT,
            french TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_translation(image_name, extracted_text, translations):
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO translations 
        (image_name, extracted_text, english, hindi, german, spanish, french)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        image_name,
        extracted_text,
        translations.get("English"),
        translations.get("Hindi"),
        translations.get("German"),
        translations.get("Spanish"),
        translations.get("French")
    ))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM translations ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows