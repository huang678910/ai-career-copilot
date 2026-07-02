"""Create the test database if it doesn't exist."""
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
with engine.connect() as conn:
    conn.execute(text("commit"))
    result = conn.execute(
        text("SELECT 1 FROM pg_database WHERE datname='career_copilot_test'")
    )
    if result.scalar():
        print("Test database already exists.")
    else:
        conn.execute(text("commit"))
        conn.execute(text("CREATE DATABASE career_copilot_test"))
        print("Created test database: career_copilot_test")
