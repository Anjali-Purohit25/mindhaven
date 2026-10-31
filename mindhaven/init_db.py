import mysql.connector
from werkzeug.security import generate_password_hash

def init_database():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password=""
        )
        cursor = conn.cursor()
        
        # Read schema
        with open("schema.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
            
        for statement in sql_script.split(";"):
            stmt = statement.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                except Exception as ex:
                    # Ignore FK seed if user 1 doesn't exist yet
                    pass
                    
        # Ensure a community system user exists for initial seeded vents
        cursor.execute("USE mindhaven_db;")
        cursor.execute("SELECT id FROM users WHERE id = 1;")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (id, username, password_hash) VALUES (1, 'community_seed', %s)",
                (generate_password_hash("community123!"),)
            )
            
        # Reseed initial vents if empty
        cursor.execute("SELECT COUNT(*) FROM vents;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO vents (user_id, content, emotion_tag, hugs_count, support_count) VALUES
                (1, 'Feeling so burned out trying to balance interviews and studying. Just need to remind myself to breathe.', 'Burnout', 14, 9),
                (1, 'Anxiety hit hard this morning for no clear reason. Doing the 4-7-8 breathing now.', 'Anxious', 21, 12),
                (1, 'To whoever is having a tough day: you have survived 100% of your worst days so far. Be gentle with yourself.', 'Hopeful', 38, 25);
            """)

        conn.commit()
        print("MindHaven database & tables initialized successfully!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

if __name__ == "__main__":
    init_database()
