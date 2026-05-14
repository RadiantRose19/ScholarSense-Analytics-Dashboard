import mysql.connector
import pandas as pd

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",           # change if you have password
        password="",           # put your MySQL password
        database="scholarsense"
    )

def save_to_mysql(df):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            subject VARCHAR(20), sex VARCHAR(2), age INT,
            total_score FLOAT, risk_score FLOAT,
            absences INT, failures INT, G3 INT
        )
    """)
    
    # Insert Data
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO students (subject, sex, age, total_score, risk_score, absences, failures, G3)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (row['subject'], row['sex'], row['age'], row['total_score'], 
              row['risk_score'], row['absences'], row['failures'], row['G3']))
    
    conn.commit()
    conn.close()
    print("Data saved to MySQL successfully!")