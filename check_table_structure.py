#!/usr/bin/env python
"""
Check the actual data structure and format in the RAW tables.
"""

import snowflake.connector
import json

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
    
    # Check CUSTOMERS table structure
    print("\n📋 CUSTOMERS table structure:")
    cur.execute('DESC TABLE BANKING.RAW.customers')
    for row in cur.fetchall():
        print(f"  {row[0]:20} | {row[1]:15} | {row[2]}")
    
    # Check ACCOUNTS table structure
    print("\n📋 ACCOUNTS table structure:")
    cur.execute('DESC TABLE BANKING.RAW.accounts')
    for row in cur.fetchall():
        print(f"  {row[0]:20} | {row[1]:15} | {row[2]}")
    
    # Check TRANSACTIONS table structure
    print("\n📋 TRANSACTIONS table structure:")
    cur.execute('DESC TABLE BANKING.RAW.transactions')
    for row in cur.fetchall():
        print(f"  {row[0]:20} | {row[1]:15} | {row[2]}")
    
    # Try a sample query on customers
    print("\n📋 Sample data from CUSTOMERS (first row):")
    cur.execute('SELECT * FROM BANKING.RAW.customers LIMIT 1')
    result = cur.fetchone()
    if result:
        print(f"  Full row: {result}")
        print(f"  Data type: {type(result[0])}")
        
        # Try to access as variant
        try:
            cur.execute('SELECT v:id FROM BANKING.RAW.customers LIMIT 1')
            variant_test = cur.fetchone()
            print(f"  ✓ Variant access works: {variant_test[0]}")
        except Exception as e:
            print(f"  ✗ Variant access failed: {e}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
