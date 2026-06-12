"""
Database module for SDPS (Student Dropout Prediction System)
Handles SQLite operations for admin authentication and prediction history
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict
import bcrypt

class Database:
    """SQLite database manager for SDPS"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        if db_path is None:
            # Use environment variable or default to current directory
            db_path = os.getenv("PERSISTENT_DB_PATH", "sdps.db")
        
        # Ensure the directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        self.db_path = db_path
        print(f"Database path: {self.db_path}")  # Debug: show the actual path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create admins table with email and profile support
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email_verified INTEGER DEFAULT 0,
                    verification_code TEXT,
                    profile_image TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    age INTEGER,
                    marital_status TEXT,
                    course TEXT,
                    application_mode TEXT,
                    attendance TEXT,
                    qualification TEXT,
                    gender TEXT,
                    displaced TEXT,
                    special_needs TEXT,
                    scholarship TEXT,
                    international TEXT,
                    risk_probability REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    priority_score REAL,
                    priority_band TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Database initialization error: {e}")
            raise
    
    # ============================================================================
    # ADMIN AUTHENTICATION METHODS
    # ============================================================================
    
    def create_admin(self, username: str, password: str, email: str = None, profile_image: str = None) -> bool:
        """
        Create a new admin user with hashed password
        Returns True if successful, False if username already exists
        """
        try:
            # Hash the password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Default email format if not provided
            default_email = f"{username}@gmail.com" if not email else email
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO admins (username, email, password_hash, profile_image) VALUES (?, ?, ?, ?)",
                (username, default_email, password_hash, profile_image)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Username already exists
            return False
    
    def verify_admin(self, username: str, password: str, email: str = None) -> bool:
        """
        Verify admin credentials with optional email verification
        Returns True if credentials are valid, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if email:
            cursor.execute(
                "SELECT password_hash, email_verified FROM admins WHERE username = ? AND email = ?",
                (username, email)
            )
        else:
            cursor.execute(
                "SELECT password_hash, email_verified FROM admins WHERE username = ?",
                (username,)
            )
        
        result = cursor.fetchone()
        conn.close()
        
        if result is None:
            return False
        
        stored_hash, email_verified = result
        
        # Handle both string and bytes for password_hash
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        
        # Verify password
        password_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        
        # For now, we'll allow login even if email not verified
        # You can change this to: return password_valid and email_verified == 1
        return password_valid
    
    def get_admin_profile(self, username: str) -> Optional[Dict]:
        """Get admin profile information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT username, email, email_verified, profile_image FROM admins WHERE username = ?",
            (username,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'username': result[0],
                'email': result[1],
                'email_verified': result[2] == 1,
                'profile_image': result[3]
            }
        return None
    
    def update_admin_profile(self, username: str, email: str = None, profile_image: str = None) -> bool:
        """Update admin profile"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if email and profile_image:
                cursor.execute(
                    "UPDATE admins SET email = ?, profile_image = ? WHERE username = ?",
                    (email, profile_image, username)
                )
            elif email:
                cursor.execute(
                    "UPDATE admins SET email = ? WHERE username = ?",
                    (email, username)
                )
            elif profile_image:
                cursor.execute(
                    "UPDATE admins SET profile_image = ? WHERE username = ?",
                    (profile_image, username)
                )
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change admin password"""
        if not self.verify_admin(username, old_password):
            return False
        
        try:
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE admins SET password_hash = ? WHERE username = ?",
                (new_hash, username)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def admin_exists(self) -> bool:
        """Check if any admin user exists in the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM admins")
            count = cursor.fetchone()[0]
            
            conn.close()
            return count > 0
        except sqlite3.OperationalError:
            return False

    def update_admin_credentials(self, username: str, password: str, email: str) -> bool:
        """Update the first admin user credentials"""
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE admins
                SET username = ?, email = ?, password_hash = ?
                WHERE id = (SELECT id FROM admins ORDER BY id LIMIT 1)
                """,
                (username, email, password_hash)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    # ============================================================================
    # PREDICTION HISTORY METHODS
    # ============================================================================
    
    def save_prediction(
        self,
        age: int,
        marital_status: str,
        risk_probability: float,
        risk_level: str,
        priority_score: float,
        priority_band: str,
        course: str = None,
        application_mode: str = None,
        attendance: str = None,
        qualification: str = None,
        gender: str = None,
        displaced: str = None,
        special_needs: str = None,
        scholarship: str = None,
        international: str = None
    ) -> int:
        """
        Save a prediction to the database
        Returns the ID of the inserted record
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO predictions (
                timestamp, age, marital_status, course, application_mode,
                attendance, qualification, gender, displaced, special_needs,
                scholarship, international, risk_probability, risk_level,
                priority_score, priority_band
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, age, marital_status, course, application_mode,
            attendance, qualification, gender, displaced, special_needs,
            scholarship, international, risk_probability, risk_level,
            priority_score, priority_band
        ))
        
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return prediction_id
    
    def get_all_predictions(self) -> List[Dict]:
        """
        Retrieve all predictions from the database
        Returns list of dictionaries with prediction data
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, timestamp, age, marital_status, course, application_mode,
                attendance, qualification, gender, displaced, special_needs,
                scholarship, international, risk_probability, risk_level,
                priority_score, priority_band
            FROM predictions
            ORDER BY id DESC
        """)
        
        columns = [
            'id', 'timestamp', 'age', 'marital', 'course', 'application_mode',
            'attendance', 'qualification', 'gender', 'displaced', 'special_needs',
            'scholarship', 'international', 'risk_prob', 'risk_level',
            'priority_score', 'priority_band'
        ]
        
        rows = cursor.fetchall()
        conn.close()
        
        predictions = []
        for row in rows:
            prediction = dict(zip(columns, row))
            predictions.append(prediction)
        
        return predictions
    
    def get_prediction_stats(self) -> Dict:
        """
        Get statistics about predictions
        Returns dictionary with counts
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total predictions
        cursor.execute("SELECT COUNT(*) FROM predictions")
        total = cursor.fetchone()[0]
        
        # High risk count
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk_level = 'HIGH RISK'")
        high_risk = cursor.fetchone()[0]
        
        # Moderate risk count
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk_level = 'MODERATE RISK'")
        moderate_risk = cursor.fetchone()[0]
        
        # Low risk count
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk_level = 'LOW RISK'")
        low_risk = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'high_risk': high_risk,
            'moderate_risk': moderate_risk,
            'low_risk': low_risk
        }
    
    def clear_all_predictions(self) -> int:
        """
        Clear all predictions from the database
        Returns number of rows deleted
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM predictions")
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def delete_prediction(self, prediction_id: int) -> bool:
        """
        Delete a specific prediction by ID
        Returns True if deleted, False if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
