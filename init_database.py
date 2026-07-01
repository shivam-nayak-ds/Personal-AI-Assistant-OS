# Database Initialization Script
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.goal import Goal
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message
from sqlalchemy import text


def init_database():
    """Initialize the database with essential tables"""
    print("🚀 Initializing Hermes AI OS database...")

    # Create tables
    try:
        print("📝 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")

    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

    # Test connection
    try:
        print("🔍 Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ Database connection successful!")

    except Exception as e:
        print(f"❌ Error testing database connection: {str(e)}")
        return False

    # Create admin user
    try:
        print("👤 Creating admin user...")
        db = engine.connect()

        # Check if admin user already exists
        check_query = text("SELECT id FROM users WHERE username = 'admin'")
        result = db.execute(check_query)
        if result.fetchone():
            print("⚠️  Admin user already exists")
            db.close()
            return True

        # Create admin user
        import bcrypt
        hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
        insert_query = text("""
            INSERT INTO users (email, username, hashed_password, is_active, is_admin, created_at)
            VALUES (:email, :username, :hashed_password, :is_active, :is_admin, :created_at)
        """)

        db.execute(insert_query, {
            'email': 'admin@hermes.ai',
            'username': 'admin',
            'hashed_password': hashed_password,
            'is_active': True,
            'is_admin': True,
            'created_at': text('NOW()')
        })

        db.commit()
        db.close()
        print("✅ Admin user created (username: admin, password: admin123)")

    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        return False

    # Create sample goals
    try:
        print("🎯 Creating sample goals...")
        db = engine.connect()

        # Check if goals exist
        check_query = text("SELECT id FROM goals WHERE user_id = (SELECT id FROM users WHERE username = 'admin')")
        result = db.execute(check_query)
        if result.fetchone():
            print("⚠️  Sample goals already exist")
            db.close()
            return True

        # Create sample goals
        goals_data = [
            ("Learn Python for AI Development", "Master Python with focus on AI/ML libraries", "active", "medium"),
            ("Build Personal AI Assistant", "Create a production-grade personal assistant", "in_progress", "high"),
            ("Read AI Research Papers", "Read and understand recent advances in AI", "active", "low"),
        ]

        for goal_data in goals_data:
            insert_query = text("""
                INSERT INTO goals (user_id, title, description, status, priority, created_at)
                VALUES (:user_id, :title, :description, :status, :priority, :created_at)
            """)

            db.execute(insert_query, {
                'user_id': db.execute(text("SELECT id FROM users WHERE username = 'admin'")).scalar(),
                'title': goal_data[0],
                'description': goal_data[1],
                'status': goal_data[2],
                'priority': goal_data[3],
                'created_at': text('NOW()')
            })

        db.commit()
        db.close()
        print("✅ Sample goals created")

    except Exception as e:
        print(f"❌ Error creating sample goals: {str(e)}")
        return False

    print("🎉 Database initialization completed successfully!")
    return True


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)