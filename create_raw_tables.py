#!/usr/bin/env python
"""
Create RAW tables in Snowflake for the banking data pipeline.
Run this script to set up the raw data layer.

Usage:
    python create_raw_tables.py
"""

import snowflake.connector
import os
from dotenv import load_dotenv

# Load environment variables if .env exists
load_dotenv()

# Snowflake Connection Parameters
config = {
    'user': 'bhandeystruck10',
    'password': 'Bh@ndeystruck199',
    'account': 'kl18145.ap-south-1.aws',
    'warehouse': 'compute_wh',
    'database': 'banking',
    'role': 'accountadmin',
}

try:
    print("Connecting to Snowflake...")
    conn = snowflake.connector.connect(**config)
    cur = conn.cursor()
    print("✓ Connected to Snowflake")
    
    # Create RAW schema
    print("\nCreating RAW schema...")
    cur.execute('CREATE SCHEMA IF NOT EXISTS BANKING.RAW')
    print("✓ RAW schema created")
    
    # Create customers table
    print("Creating BANKING.RAW.customers table...")
    cur.execute('''
        CREATE TABLE IF NOT EXISTS BANKING.RAW.customers (
            v VARIANT
        )
    ''')
    print("✓ customers table created")
    
    # Create accounts table
    print("Creating BANKING.RAW.accounts table...")
    cur.execute('''
        CREATE TABLE IF NOT EXISTS BANKING.RAW.accounts (
            v VARIANT
        )
    ''')
    print("✓ accounts table created")
    
    # Create transactions table
    print("Creating BANKING.RAW.transactions table...")
    cur.execute('''
        CREATE TABLE IF NOT EXISTS BANKING.RAW.transactions (
            v VARIANT
        )
    ''')
    print("✓ transactions table created")
    
    # Verify tables
    print("\nVerifying tables...")
    cur.execute('SHOW TABLES IN SCHEMA BANKING.RAW')
    tables = cur.fetchall()
    print(f"✓ Created {len(tables)} tables in BANKING.RAW:")
    for table in tables:
        print(f"  - {table[1]}")
    
    cur.close()
    conn.close()
    print("\n✅ Raw tables setup completed successfully!")
    print("You can now run: dbt run")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
