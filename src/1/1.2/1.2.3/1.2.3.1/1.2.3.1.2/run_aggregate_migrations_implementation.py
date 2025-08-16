import sqlite3

# Define migrations chronologically. These scripts create a source table
# ('sales') and a corresponding aggregate table ('daily_sales_summary'),
# and include logic for the initial data population.
MIGRATIONS = {
    "0001_create_source_sales_table": """
    CREATE TABLE sales (
        id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        sale_date TEXT NOT NULL,
        amount REAL NOT NULL
    );
    """,
    "0002_create_aggregate_sales_summary": """
    CREATE TABLE daily_sales_summary (
        summary_date TEXT PRIMARY KEY,
        total_sales REAL NOT NULL,
        transaction_count INTEGER NOT NULL
    );
    """,
    # This migration populates the aggregate table. In a real system,
    # this logic might be run periodically by a separate process (e.g., a nightly job)
    # to keep the aggregate table up-to-date.
    "0003_populate_daily_sales_summary": """
    INSERT INTO daily_sales_summary (summary_date, total_sales, transaction_count)
    SELECT
        sale_date,
        SUM(amount),
        COUNT(id)
    FROM
        sales
    GROUP BY
        sale_date;
    """
}

def run_aggregate_migrations(db_path="aggregates.db"):
    """
    Applies a set of ordered SQL migrations to a database.

    This function simulates a simple database migration system, ideal for
    creating and maintaining the schema of aggregate tables. It works by:
    1.  Connecting to a SQLite database.
    2.  Creating a `migration_log` table if it doesn't exist to track
        which migrations have already been applied.
    3.  Reading a predefined dictionary of named SQL scripts (`MIGRATIONS`).
    4.  Executing each script in order, skipping any that are already logged
        as applied.
    5.  Logging each newly applied script to the `migration_log` table.

    This ensures that database schema changes, especially for summary or
    aggregate tables, are applied consistently and exactly once.

    Args:
        db_path (str): The file path for the SQLite database.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Step 1: Ensure the migration tracking table exists.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_log (
                migration_name TEXT PRIMARY KEY,
                applied_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

        # Step 2: Get the set of already applied migrations.
        cursor.execute("SELECT migration_name FROM migration_log;")
        applied_migrations = {row[0] for row in cursor.fetchall()}
        print(f"Already applied migrations: {applied_migrations or 'None'}")

        # Step 3: Iterate through defined migrations and apply new ones.
        # Sorting ensures migrations are applied in chronological order.
        for name in sorted(MIGRATIONS.keys()):
            if name not in applied_migrations:
                print(f"Applying migration: {name}...")
                try:
                    # Execute the migration script.
                    sql_script = MIGRATIONS[name]
                    cursor.executescript(sql_script)

                    # Record the successful migration.
                    cursor.execute(
                        "INSERT INTO migration_log (migration_name) VALUES (?);", (name,)
                    )

                    # Commit the transaction for this migration.
                    conn.commit()
                    print(f"-> Successfully applied and logged {name}.")
                except sqlite3.Error as e:
                    print(f"-> ERROR applying migration {name}: {e}")
                    # If a migration fails, roll back its changes and stop.
                    conn.rollback()
                    raise e
            else:
                print(f"Skipping already applied migration: {name}")

    except sqlite3.Error as e:
        print(f"A database error occurred: {e}")
    finally:
        if conn:
            conn.close()
        print("Migration process finished.")