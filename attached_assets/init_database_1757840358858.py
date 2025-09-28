#!/usr/bin/env python3
"""
Initialize the PostgreSQL database for Excel Mock Interviewer
Creates all tables and sets up the database schema
"""

import sys
import logging
from services.database_service import DatabaseService

def main():
    """Initialize the database schema"""
    try:
        print("Initializing Excel Mock Interviewer database...")
        
        # Create database service instance (this will create tables automatically)
        db_service = DatabaseService()
        
        print("✅ Database schema created successfully!")
        print("✅ All tables are ready for use")
        
        # Test basic database operations
        print("\n🔍 Testing database connection...")
        
        # Test candidate creation
        candidate_id = db_service.create_or_get_candidate(
            name="Test User", 
            experience_level="Intermediate (1-3 years)"
        )
        print(f"✅ Test candidate created with ID: {candidate_id}")
        
        # Test analytics (should return empty but not error)
        analytics = db_service.get_interview_analytics(days=30)
        print(f"✅ Analytics query successful: {analytics['total_interviews']} interviews found")
        
        print("\n🎉 Database initialization complete!")
        print("The application is ready to store interview data persistently.")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        logging.error(f"Database initialization error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()