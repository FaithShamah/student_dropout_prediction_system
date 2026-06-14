"""
Migration script to import prediction_history.csv into Supabase database
Run this once to migrate your old CSV data to the new database system
"""

import os
import pandas as pd
from database import Database
from datetime import datetime


def migrate_csv_to_database():
    """Import CSV predictions into Supabase database"""
    
    csv_file = os.path.join(os.path.dirname(__file__), "prediction_history.csv")
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print("❌ No prediction_history.csv found. Nothing to migrate.")
        return
    
    # Initialize database
    try:
        db = Database()
        print("✅ Supabase connected")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return
    
    # Read CSV file
    try:
        df = pd.read_csv(csv_file)
        print(f"📄 Found {len(df)} records in CSV file")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return
    
    # Check if database already has predictions
    existing_predictions = db.get_all_predictions()
    if existing_predictions:
        response = input(f"⚠️  Database already has {len(existing_predictions)} predictions. Continue anyway? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Migration cancelled")
            return
    
    # Migrate each record
    migrated_count = 0
    skipped_count = 0
    
    for idx, row in df.iterrows():
        try:
            timestamp = row.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            age = int(row.get('age', 0)) if pd.notna(row.get('age')) else None
            marital_status = str(row.get('marital', '')) if pd.notna(row.get('marital')) else None
            course = str(row.get('course', '')) if pd.notna(row.get('course')) else None
            qualification = str(row.get('qualification', '')) if pd.notna(row.get('qualification')) else None
            
            # --- ADD EXTRACTION HERE ---
            application_order = int(row.get('application_order', 0)) if pd.notna(row.get('application_order')) else None
            
            risk_prob = float(row.get('risk_prob', 0.0)) if pd.notna(row.get('risk_prob')) else 0.0
            risk_level = str(row.get('risk_level', 'UNKNOWN')) if pd.notna(row.get('risk_level')) else 'UNKNOWN'
            priority_score = float(row.get('priority_score', 0.0)) if pd.notna(row.get('priority_score')) else 0.0
            priority_band = str(row.get('priority_band', 'P4 - Routine')) if pd.notna(row.get('priority_band')) else 'P4 - Routine'
            
            # Save to database
            db.save_prediction(
                age=age,
                marital_status=marital_status,
                course=course,
                qualification=qualification,
                application_order=application_order, 
                risk_probability=risk_prob,
                risk_level=risk_level,
                priority_score=priority_score,
                priority_band=priority_band
            )
            
            migrated_count += 1
            print(f"✓ Migrated record {idx + 1}/{len(df)}")
            
        except Exception as e:
            print(f"⚠️  Skipped record {idx + 1}: {e}")
            skipped_count += 1
            continue
    
    print("\n" + "="*60)
    print("📊 Migration Summary:")
    print(f"   ✅ Successfully migrated: {migrated_count} records")
    print(f"   ⚠️  Skipped: {skipped_count} records")
    print(f"   📈 Total in database: {len(db.get_all_predictions())} records")
    print("="*60)
    
    response = input("\n🗑️  Delete old CSV file? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        try:
            backup_file = csv_file + ".backup"
            os.rename(csv_file, backup_file)
            print(f"✅ CSV file backed up to: {backup_file}")
        except Exception as e:
            print(f"❌ Could not backup CSV: {e}")


if __name__ == "__main__":
    print("="*60)
    print("🔄 SDPS Data Migration Tool")
    print("   CSV → Supabase Database")
    print("="*60)
    print()
    
    migrate_csv_to_database()
    
    print("\n✨ Migration complete! You can now run the main app.")