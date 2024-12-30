import sqlite3

def migrate_database():
    # Connect to the database
    conn = sqlite3.connect('livemap.db')
    cursor = conn.cursor()

    try:
        # Add is_active column to event table
        cursor.execute('''
            ALTER TABLE event
            ADD COLUMN is_active BOOLEAN DEFAULT 1
        ''')
        
        # Commit the changes
        conn.commit()
        print("Successfully added is_active column to event table")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column is_active already exists")
        else:
            raise e
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
