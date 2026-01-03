"""Test database connection and setup"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def test_connection():
    """Test PostgreSQL connection with admin password"""
    try:
        # Try to connect to postgres database first
        print("Testing connection to PostgreSQL...")
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="admin",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='land_optimization'")
        exists = cursor.fetchone()

        if not exists:
            print("Creating land_optimization database...")
            cursor.execute("CREATE DATABASE land_optimization")
            print("✓ Database created successfully!")
        else:
            print("✓ Database 'land_optimization' already exists")

        cursor.close()
        conn.close()

        # Test connection to the land_optimization database
        print("\nTesting connection to land_optimization database...")
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="admin",
            database="land_optimization"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✓ Connected successfully!")
        print(f"✓ PostgreSQL version: {version.split(',')[0]}")

        cursor.close()
        conn.close()

        print("\n✅ Database configuration is correct!")
        print("   Host: localhost:5432")
        print("   Database: land_optimization")
        print("   User: postgres")
        print("   Password: admin")

        return True

    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure PostgreSQL service is running")
        print("2. Verify the password is set to 'admin' for postgres user")
        print("3. Run this command in psql:")
        print("   ALTER USER postgres WITH PASSWORD 'admin';")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
