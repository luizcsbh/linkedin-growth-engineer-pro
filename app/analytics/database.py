import sqlite3
import os
from datetime import datetime
from app.core.config import Config
from app.utils.logger import setup_logger

logger = setup_logger('database')

class DatabaseManager:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize the database and create tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Executions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration_seconds INTEGER,
                    status TEXT
                )
            ''')
            
            # Actions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    action_type TEXT,
                    result_score REAL,
                    detail_url TEXT,
                    detail_title TEXT,
                    is_php_relevant BOOLEAN DEFAULT 0,
                    FOREIGN KEY (execution_id) REFERENCES executions (id)
                )
            ''')
            
            # Engagement scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS engagement_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT UNIQUE,
                    weight REAL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Daily metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE,
                    growth_score REAL,
                    ssi_score REAL,
                    consistency_score REAL,
                    activity_count INTEGER
                )
            ''')
            
            # Initialize default engagement weights
            default_weights = [
                ('jobs_view', 2.0),
                ('profile_visit', 4.0),
                ('post_like', 1.0),
                ('company_follow', 3.0)
            ]
            
            for action_type, weight in default_weights:
                cursor.execute('''
                    INSERT OR IGNORE INTO engagement_scores (action_type, weight)
                    VALUES (?, ?)
                ''', (action_type, weight))
            
            # Optimization tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS optimization_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logger.info("Database initialized successfully.")

    def log_execution(self, duration, status):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO executions (duration_seconds, status) VALUES (?, ?)', (duration, status))
            conn.commit()
            return cursor.lastrowid

    def log_action(self, execution_id, action_type, result_score, detail_url=None, detail_title=None, is_php_relevant=0):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO actions (execution_id, action_type, result_score, detail_url, detail_title, is_php_relevant) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (execution_id, action_type, result_score, detail_url, detail_title, is_php_relevant))
            conn.commit()

    def get_recent_actions(self, limit=20, action_types=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if action_types:
                placeholders = ', '.join(['?'] * len(action_types))
                query = f'''
                    SELECT action_type, timestamp, detail_url, detail_title, is_php_relevant 
                    FROM actions 
                    WHERE action_type IN ({placeholders})
                    ORDER BY timestamp DESC 
                    LIMIT ?
                '''
                cursor.execute(query, (*action_types, limit))
            else:
                cursor.execute('''
                    SELECT action_type, timestamp, detail_url, detail_title, is_php_relevant 
                    FROM actions 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            return cursor.fetchall()

    def get_action_stats(self, action_types):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ', '.join(['?'] * len(action_types))
            query = f'''
                SELECT action_type, COUNT(*), SUM(is_php_relevant)
                FROM actions 
                WHERE action_type IN ({placeholders})
                GROUP BY action_type
            '''
            cursor.execute(query, action_types)
            return cursor.fetchall()

    def get_engagement_weights(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT action_type, weight FROM engagement_scores')
            return dict(cursor.fetchall())

    def update_engagement_weight(self, action_type, weight):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE engagement_scores SET weight = ?, last_updated = CURRENT_TIMESTAMP WHERE action_type = ?', 
                           (weight, action_type))
            conn.commit()

    def update_daily_metrics(self, date, growth_score, ssi_score, consistency_score, activity_count):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO daily_metrics (date, growth_score, ssi_score, consistency_score, activity_count)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    growth_score = excluded.growth_score,
                    ssi_score = excluded.ssi_score,
                    consistency_score = excluded.consistency_score,
                    activity_count = excluded.activity_count
            ''', (date, growth_score, ssi_score, consistency_score, activity_count))
            conn.commit()
            
    def get_recent_metrics(self, days=7):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM daily_metrics ORDER BY date DESC LIMIT ?', (days,))
            return cursor.fetchall()

    def get_last_optimization_date(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp FROM optimization_log ORDER BY timestamp DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                return datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
            return None

    def update_last_optimization_date(self, timestamp):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO optimization_log (timestamp) VALUES (?)", (timestamp.strftime('%Y-%m-%d %H:%M:%S'),))
            conn.commit()
