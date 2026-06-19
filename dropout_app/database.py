"""
Database module for SDPS (Student Dropout Prediction System)
Handles Supabase operations for admin authentication and prediction history
"""

import os
from datetime import datetime
from typing import Optional, List, Dict
import bcrypt
from supabase import create_client, Client


class Database:
    """Supabase database manager for SDPS"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """Initialize Supabase client"""
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Supabase URL and Key must be provided. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
            )
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        print(f"Supabase connected: {self.supabase_url}")
    
    # Return (success, error_message)
    def _handle_error(self, error) -> str:
        """Handle Supabase errors and return message"""
        msg = ""
        if hasattr(error, 'message'):
            msg = str(error.message)
        else:
            msg = str(error)
        print(f"Supabase error: {msg}")
        return msg
    
    # ============================================================================
    # ADMIN AUTHENTICATION METHODS
    # ============================================================================
    
    def create_admin(
        self, 
        username: str, 
        password: str, 
        email: str = None, 
        profile_image: str = None
    ) -> bool:
        """
        Create a new admin user with hashed password
        Returns True if successful, False if username already exists
        """
        try:
            # Hash the password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Default email format if not provided
            default_email = f"{username}@gmail.com" if not email else email
            
            response = self.client.table('admins').insert({
                'username': username,
                'email': default_email,
                'password_hash': password_hash,
                'profile_image': profile_image
            }).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            self._handle_error(e)
            # Check for unique constraint violation
            if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                return False
            return False
    
    def verify_admin(self, username: str, password: str, email: str = None) -> bool:
        """
        Verify admin credentials with optional email verification
        Returns True if credentials are valid, False otherwise
        """
        try:
            if email:
                response = self.client.table('admins').select(
                    'password_hash, email_verified'
                ).eq('email', email).execute()
            else:
                response = self.client.table('admins').select(
                    'password_hash, email_verified'
                ).eq('username', username).execute()
            
            if not response.data or len(response.data) == 0:
                return False
            
            stored_hash = response.data[0]['password_hash']
            
            # Handle string password hash
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            
            # Verify password
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
            
        except Exception as e:
            self._handle_error(e)
            return False
    
    def get_admin_profile(self, username: str) -> Optional[Dict]:
        """Get admin profile information"""
        try:
            response = self.client.table('admins').select(
                'username, email, email_verified, profile_image'
            ).eq('username', username).execute()
            
            if response.data and len(response.data) > 0:
                data = response.data[0]
                return {
                    'username': data['username'],
                    'email': data['email'],
                    'email_verified': data['email_verified'] == 1 or data['email_verified'] is True,
                    'profile_image': data['profile_image']
                }
            return None
            
        except Exception as e:
            self._handle_error(e)
            return None

    def get_current_profile(self, username: str, account_type: str) -> Optional[Dict]:
        """Helper to get profile dynamically based on account type"""
        if account_type == 'user':
            return self.get_user_profile(username)
        return self.get_admin_profile(username)
    
    def update_admin_profile(
        self, 
        username: str, 
        email: str = None, 
        profile_image: str = None
    ) -> bool:
        """Update admin profile"""
        try:
            update_data = {}
            if email:
                update_data['email'] = email
            if profile_image:
                update_data['profile_image'] = profile_image
            
            if not update_data:
                return True
            
            response = self.client.table('admins').update(
                update_data
            ).eq('username', username).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            self._handle_error(e)
            return False
    
    def change_password(
        self, 
        username: str, 
        old_password: str, 
        new_password: str
    ) -> bool:
        """Change admin password"""
        if not self.verify_admin(username, old_password):
            return False
        
        try:
            new_hash = bcrypt.hashpw(
                new_password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            response = self.client.table('admins').update({
                'password_hash': new_hash
            }).eq('username', username).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            self._handle_error(e)
            return False
    
    def admin_exists(self) -> bool:
        """Check if any admin user exists in the database"""
        try:
            response = self.client.table('admins').select('id').limit(1).execute()
            return len(response.data) > 0
        except Exception as e:
            self._handle_error(e)
            return False
    
    def update_admin_credentials(
        self, 
        username: str, 
        password: str, 
        email: str
    ) -> bool:
        """Update the first admin user credentials"""
        try:
            password_hash = bcrypt.hashpw(
                password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Get the first admin's ID
            response = self.client.table('admins').select('id').limit(1).execute()
            
            if not response.data:
                return False
            
            first_admin_id = response.data[0]['id']
            
            # Update the credentials
            self.client.table('admins').update({
                'username': username,
                'email': email,
                'password_hash': password_hash
            }).eq('id', first_admin_id).execute()
            
            return True
            
        except Exception as e:
            self._handle_error(e)
            return False

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str = None,
        profile_image: str = None
    ) -> tuple[bool, str]:
        """Create a regular user account in the users table."""
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            response = self.client.table('users').insert({
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'full_name': full_name or username,
                'profile_image': profile_image
            }).execute()
            return True, "Account created successfully" if response.data else "Account creation returned no data"
        except Exception as e:
            message = self._handle_error(e)
            if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                return False, "A user with this username or email already exists."
            return False, message or "Could not create account."

    def verify_user(self, username_or_email: str, password: str) -> tuple[bool, str | None]:
        """Verify a regular user by username or email."""
        try:
            response = self.client.table('users').select(
                'username, password_hash, email_verified'
            ).eq('username', username_or_email).execute()

            if not response.data:
                response = self.client.table('users').select(
                    'username, password_hash, email_verified'
                ).eq('email', username_or_email).execute()

            if not response.data:
                return False, None

            stored_hash = response.data[0]['password_hash']
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return True, response.data[0]['username']
            return False, None
        except Exception as e:
            self._handle_error(e)
            return False, None

    def verify_user_or_admin(self, username_or_email: str, password: str) -> tuple[bool, str | None, str | None, str]:
        """Verify either a regular user or an admin account."""
        user_verified, user_name = self.verify_user(username_or_email, password)
        if user_verified:
            return True, user_name, "user", "Welcome back"

        email_lookup = username_or_email if "@" in username_or_email else None
        admin_verified = self.verify_admin(username_or_email, password, email=email_lookup)
        if admin_verified:
            return True, username_or_email, "admin", "Welcome back"

        return False, None, None, "Invalid username/email or password."

    def get_user_profile(self, username: str) -> Optional[Dict]:
        """Get regular user profile information."""
        try:
            response = self.client.table('users').select(
                'username, email, full_name, email_verified, profile_image'
            ).eq('username', username).execute()

            if response.data:
                data = response.data[0]
                return {
                    'username': data['username'],
                    'email': data['email'],
                    'full_name': data.get('full_name') or data['username'],
                    'email_verified': data['email_verified'] == 1 or data['email_verified'] is True,
                    'profile_image': data['profile_image']
                }
            return None
        except Exception as e:
            self._handle_error(e)
            return None

    def change_user_password(
        self,
        username: str,
        old_password: str,
        new_password: str
    ) -> tuple[bool, str]:
        """Change a regular user's password."""
        verified, _ = self.verify_user(username, old_password)
        if not verified:
            return False, "Current password is incorrect"

        try:
            new_hash = bcrypt.hashpw(
                new_password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            response = self.client.table('users').update({
                'password_hash': new_hash
            }).eq('username', username).execute()

            return (len(response.data) > 0), "Password updated successfully" if response.data else "Could not update password."
        except Exception as e:
            return False, self._handle_error(e) or "Could not update password."

    def get_current_profile(self, username: str, account_type: str) -> Optional[Dict]:
        """Return the current admin or user profile."""
        if account_type == "user":
            return self.get_user_profile(username)
        return self.get_admin_profile(username)

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email to help with password reset."""
        try:
            response = self.client.table('users').select('*').eq('email', email).execute()
            if response.data:
                return response.data[0]
            
            response = self.client.table('admins').select('*').eq('email', email).execute()
            if response.data:
                data = response.data[0]
                data['is_admin'] = True
                return data
            return None
        except Exception as e:
            self._handle_error(e)
            return None

    def set_verification_code(self, username_or_email: str, code: str) -> bool:
        """Save a verification code for a user or admin."""
        try:
            # Try users first
            response = self.client.table('users').update({'verification_code': code}).eq('username', username_or_email).execute()
            if not response.data:
                response = self.client.table('users').update({'verification_code': code}).eq('email', username_or_email).execute()
            
            # If not in users, try admins
            if not response.data:
                response = self.client.table('admins').update({'verification_code': code}).eq('username', username_or_email).execute()
                if not response.data:
                    response = self.client.table('admins').update({'verification_code': code}).eq('email', username_or_email).execute()
            
            return len(response.data) > 0
        except Exception as e:
            self._handle_error(e)
            return False

    def verify_email_code(self, username: str, code: str) -> bool:
        """Verify the OTP code and set email_verified to True."""
        try:
            # Check users
            response = self.client.table('users').select('verification_code').eq('username', username).execute()
            is_admin = False
            if not response.data:
                response = self.client.table('admins').select('verification_code').eq('username', username).execute()
                is_admin = True

            if not response.data:
                return False

            stored_code = response.data[0].get('verification_code')
            if stored_code and stored_code == code:
                table = 'admins' if is_admin else 'users'
                # Clear code and set verified
                self.client.table(table).update({
                    'verification_code': None,
                    'email_verified': True
                }).eq('username', username).execute()
                return True
            return False
        except Exception as e:
            self._handle_error(e)
            return False

    def reset_password_with_code(self, email: str, code: str, new_password: str) -> tuple[bool, str]:
        """Reset password using the OTP code."""
        try:
            user_data = self.get_user_by_email(email)
            if not user_data:
                return False, "User not found."

            if user_data.get('verification_code') != code:
                return False, "Invalid or expired verification code."

            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            table = 'admins' if user_data.get('is_admin') else 'users'

            self.client.table(table).update({
                'password_hash': new_hash,
                'verification_code': None
            }).eq('email', email).execute()

            return True, "Password reset successfully."
        except Exception as e:
            return False, self._handle_error(e)

    def get_all_users(self) -> List[Dict]:
        """Get all regular users for admin dashboard."""
        try:
            response = self.client.table('users').select('id, username, email, full_name, email_verified, created_at').execute()
            return response.data if response.data else []
        except Exception as e:
            self._handle_error(e)
            return []

    def delete_user(self, username: str) -> bool:
        """Delete a regular user account."""
        try:
            response = self.client.table('users').delete().eq('username', username).execute()
            return len(response.data) > 0
        except Exception as e:
            self._handle_error(e)
            return False

    def move_user_to_ledger(self, username: str) -> bool:
        """Move a regular user from users to user_ledger table instead of hard-deleting."""
        try:
            user_resp = self.client.table('users').select('*').eq('username', username).execute()
            if not user_resp.data:
                return False
            user_data = user_resp.data[0]
            ledger_payload = {
                'original_user_id': user_data.get('id'),
                'username': user_data.get('username'),
                'email': user_data.get('email'),
                'full_name': user_data.get('full_name'),
                'email_verified': user_data.get('email_verified'),
                'profile_image': user_data.get('profile_image'),
                'created_at': user_data.get('created_at'),
                'moved_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.client.table('user_ledger').insert(ledger_payload).execute()
            self.client.table('users').delete().eq('id', user_data.get('id')).execute()
            return True
        except Exception as e:
            self._handle_error(e)
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
        application_order: int = None,
        attendance: str = None,
        qualification: str = None,
        gender: str = None,
        scholarship: str = None,
        international: str = None
    ) -> tuple:
        """
        Save a prediction to the database
        Returns (success: bool, error_message: str | None)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            response = self.client.table('predictions').insert({
                'timestamp': timestamp,
                'age': age,
                'marital_status': marital_status,
                'course': course,
                'application_mode': application_mode,
                'application_order': application_order,
                'attendance': attendance,
                'qualification': qualification,
                'gender': gender,
                'scholarship': scholarship,
                'international': international,
                'risk_probability': risk_probability,
                'risk_level': risk_level,
                'priority_score': priority_score,
                'priority_band': priority_band
            }).execute()
            
            if response.data and len(response.data) > 0:
                return True, None
            return False, "Insert returned no data"
            
        except Exception as e:
            err = self._handle_error(e)
            return False, err
    
    def get_all_predictions(self) -> List[Dict]:
        """
        Retrieve all predictions from the database
        Returns list of dictionaries with prediction data
        """
        try:
            response = self.client.table('predictions').select('*').order('id', desc=True).execute()
            
            predictions = []
            for row in response.data:
                prediction = {
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'age': row['age'],
                    'marital': row['marital_status'],
                    'course': row['course'],
                    'application_mode': row['application_mode'],
                    'application_order': row.get('application_order'),
                    'attendance': row['attendance'],
                    'qualification': row['qualification'],
                    'gender': row['gender'],
                    'scholarship': row['scholarship'],
                    'international': row['international'],
                    'risk_prob': row['risk_probability'],
                    'risk_level': row['risk_level'],
                    'priority_score': row['priority_score'],
                    'priority_band': row['priority_band']
                }
                predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            err = self._handle_error(e)
            print(f"Failed to load predictions: {err}")
            return []
        
    def get_prediction_stats(self) -> Dict:
        """
        Get statistics about predictions
        Returns dictionary with counts
        """
        try:
            response = self.client.table('predictions').select('risk_level').execute()
            
            total = len(response.data)
            high_risk = sum(1 for r in response.data if r['risk_level'] == 'HIGH RISK')
            moderate_risk = sum(1 for r in response.data if r['risk_level'] == 'MODERATE RISK')
            low_risk = sum(1 for r in response.data if r['risk_level'] == 'LOW RISK')
            
            return {
                'total': total,
                'high_risk': high_risk,
                'moderate_risk': moderate_risk,
                'low_risk': low_risk
            }
            
        except Exception as e:
            err = self._handle_error(e)
            print(f"Failed to load stats: {err}")
            return {
                'total': 0,
                'high_risk': 0,
                'moderate_risk': 0,
                'low_risk': 0
            }
    
    def clear_all_predictions(self) -> int:
        """
        Clear all predictions from the database
        Returns number of rows deleted
        """
        try:
            # First get the count
            response = self.client.table('predictions').select('id', count='exact').execute()
            count = response.count if hasattr(response, 'count') else len(response.data)
            
            # Delete all
            self.client.table('predictions').delete().neq('id', 0).execute()
            
            return count
            
        except Exception as e:
            self._handle_error(e)
            return 0
    
    def delete_prediction(self, prediction_id: int) -> bool:
        """
        Delete a specific prediction by ID
        Returns True if deleted, False if not found
        """
        try:
            response = self.client.table('predictions').delete().eq('id', prediction_id).execute()
            return len(response.data) > 0
        except Exception as e:
            self._handle_error(e)
            return False