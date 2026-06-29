"""
Quick test script to verify database connection.

Run this to test if Day 3 setup is working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import (
    check_database_health,
    get_pool_stats,
    get_db,
)
from app.core.logger import get_logger

logger = get_logger(__name__)


def test_database_connection():
    """Test basic database connection."""
    print("\n" + "="*50)
    print("Testing Database Connection")
    print("="*50 + "\n")
    
    # Test 1: Health check
    print("Test 1: Health Check")
    is_healthy = check_database_health()
    if is_healthy:
        print("✅ Database is healthy!")
    else:
        print("❌ Database health check failed!")
        return False
    
    # Test 2: Pool stats
    print("\nTest 2: Connection Pool Stats")
    try:
        stats = get_pool_stats()
        print(f"  Pool size: {stats['pool_size']}")
        print(f"  Checked in (available): {stats['checked_in']}")
        print(f"  Checked out (in use): {stats['checked_out']}")
        print(f"  Overflow: {stats['overflow']}")
        print(f"  Total connections: {stats['total_connections']}")
        print("✅ Pool stats retrieved!")
    except Exception as e:
        print(f"❌ Failed to get pool stats: {str(e)}")
        return False
    
    # Test 3: Session creation and query
    print("\nTest 3: Session Creation and Query")
    try:
        db = next(get_db())
        result = db.execute("SELECT 1 as test")
        value = result.scalar()
        db.close()
        
        if value == 1:
            print(f"✅ Query executed successfully! Result: {value}")
        else:
            print(f"❌ Unexpected query result: {value}")
            return False
    except Exception as e:
        print(f"❌ Session creation failed: {str(e)}")
        return False
    
    # Test 4: Multiple sessions (test pool)
    print("\nTest 4: Multiple Sessions (Pool Test)")
    try:
        sessions = []
        for i in range(5):
            db = next(get_db())
            sessions.append(db)
        
        print(f"  Created {len(sessions)} sessions")
        
        # Check pool stats
        stats = get_pool_stats()
        print(f"  Checked out: {stats['checked_out']} (should be 5)")
        
        # Close all sessions
        for db in sessions:
            db.close()
        
        # Check pool stats again
        stats = get_pool_stats()
        print(f"  After closing: Checked out: {stats['checked_out']} (should be 0)")
        print("✅ Connection pool working correctly!")
    except Exception as e:
        print(f"❌ Pool test failed: {str(e)}")
        return False
    
    print("\n" + "="*50)
    print("All Tests Passed! ✅")
    print("="*50 + "\n")
    return True


if __name__ == "__main__":
    try:
        success = test_database_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test script failed: {str(e)}", exc_info=True)
        print(f"\n❌ Test failed with error: {str(e)}")
        sys.exit(1)
