#!/usr/bin/env python3
"""
Database initialization script for AI Excel Mock Interviewer
Run this script to set up the database tables and initial data
"""

import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize the database with tables and sample data"""
    try:
        # Import database service
        from services.database_service import DatabaseService
        
        logger.info("Initializing database...")
        
        # Create database service instance
        db_service = DatabaseService()
        
        logger.info("Database tables created successfully!")
        
        # Get basic stats
        stats = db_service.get_interview_stats()
        logger.info(f"Database stats: {stats}")
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please set the following environment variables:")
        for var in missing_vars:
            logger.info(f"  {var}=<your_value>")
        return False
    
    return True

def create_sample_data():
    """Create some sample data for testing (optional)"""
    try:
        from services.database_service import DatabaseService
        
        db_service = DatabaseService()
        
        # Create a sample candidate
        candidate_id = db_service.create_or_get_candidate(
            name="Sample User",
            experience_level="Intermediate",
            email="sample@example.com"
        )
        
        logger.info(f"Created sample candidate with ID: {candidate_id}")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")

def main():
    """Main function"""
    print("🚀 AI Excel Mock Interviewer - Database Initialization")
    print("=" * 60)
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Initialize database
    if initialize_database():
        print("✅ Database initialization completed successfully!")
        
        # Ask if user wants to create sample data
        while True:
            response = input("\n📝 Would you like to create sample data for testing? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                create_sample_data()
                print("✅ Sample data created!")
                break
            elif response in ['n', 'no']:
                print("⏭️  Skipping sample data creation.")
                break
            else:
                print("Please enter 'y' for yes or 'n' for no.")
        
        print("\n🎯 Your AI Excel Mock Interviewer is ready to use!")
        print("Run 'streamlit run app.py' to start the application.")
        
    else:
        print("❌ Database initialization failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
