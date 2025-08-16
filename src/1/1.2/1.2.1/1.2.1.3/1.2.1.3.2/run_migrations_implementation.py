import sqlite3
import os

def run_migrations(db_path, migrations_dir):
    """
    Applies database migrations from a specified directory to an SQLite database.

    This function connects to an SQLite database, checks for a `schema_migrations`
    table to track applied migrations, and applies any new, unapplied SQL migration
    files found in the given directory. Migrations are applied in alphabetical order
    of their filenames.

    Args:
        db_path (str): The path to the SQLite database file.
        migrations_dir (str): The path to the directory containing .sql migration files.
    """
    conn = None
    try:
        # Connect to the database. It will be created if it doesn't exist.
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Step 1: Create the schema_migrations table if it doesn't exist.
        # This table tracks which migrations have already been applied.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT NOT NULL PRIMARY KEY
            )
        """)
        conn.commit()

        # Step 2: Get the set of already applied migrations.
        cursor.execute("SELECT version FROM schema_migrations")
        applied_migrations = {row[0] for row in cursor.fetchall()}

        # Step 3: Find all migration files in the migrations directory.
        try:
            migration_files = sorted(
                f for f in os.listdir(migrations_dir) if f.endswith('.sql')
            )
        except FileNotFoundError:
            print(f"Error: Migrations directory '{migrations_dir}' not found.")
            return

        # Step 4: Apply any migrations that haven't been applied yet.
        migrations_to_apply = [f for f in migration_files if f not in applied_migrations]

        if not migrations_to_apply:
            print("Database is up to date.")
            return

        for migration_file in migrations_to_apply:
            print(f"Applying migration: {migration_file}...")
            try:
                # Read the migration file content
                filepath = os.path.join(migrations_dir, migration_file)
                with open(filepath, 'r') as f:
                    sql_script = f.read()

                # Execute the SQL script. executescript can handle multiple statements.
                cursor.executescript(sql_script)

                # Record the migration as applied in the same transaction
                cursor.execute(
                    "INSERT INTO schema_migrations (version) VALUES (?)",
                    (migration_file,)
                )
                
                # Commit the transaction for the current migration
                conn.commit()
                print(f"Successfully applied {migration_file}")

            except sqlite3.Error as e:
                print(f"Error applying migration {migration_file}: {e}")
                conn.rollback()  # Rollback changes if a migration fails
                return # Stop processing further migrations

        print("All new migrations applied successfully.")

    except sqlite3.Error as e:
        print(f"A database error occurred: {e}")
    finally:
        if conn:
            conn.close()