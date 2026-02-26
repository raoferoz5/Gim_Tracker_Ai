import sqlite3


class Database:

    def __init__(self):
        self.conn = sqlite3.connect("gym.db")
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT,
            exercise TEXT,
            date TEXT,
            weight REAL,
            sets INTEGER,
            reps INTEGER,
            rest_time INTEGER,
            volume REAL
        )
        """)
        self.conn.commit()

    def insert_workout(self, data):
        self.cursor.execute("""
        INSERT INTO workout_logs
        (day, exercise, date, weight, sets, reps, rest_time, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        self.conn.commit()

    def get_exercise_data(self, exercise):
        self.cursor.execute("""
        SELECT date, weight, volume
        FROM workout_logs
        WHERE exercise=?
        ORDER BY date
        """, (exercise,))
        return self.cursor.fetchall()

    def get_total_workouts(self):
        self.cursor.execute("SELECT COUNT(*) FROM workout_logs")
        return self.cursor.fetchone()[0]