#!/usr/bin/env python
"""
Test different parts of the SQL to isolate the issue
"""

import snowflake.connector

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
    
    # Test 1: Just the SELECT query
    print("\n🧪 Test 1: Just the SELECT part...")
    sql1 = '''
with ranked as (
    select
        v:id::string            as customer_id,
        v:first_name::string    as first_name,
        v:last_name::string     as last_name,
        v:email::string         as email,
        v:created_at::timestamp as created_at,
        current_timestamp()       as load_timestamp,
        row_number() over (
            partition by v:id::string
            order by v:created_at desc
        ) as rn
    from banking.raw.customers
)

select
    customer_id,
    first_name,
    last_name,
    email,
    created_at,
    load_timestamp
from ranked
where rn = 1
    '''
    try:
        cur.execute(sql1)
        result = cur.fetchone()
        print(f"  ✓ SELECT works! Row: {result[:3]}...")
    except Exception as e:
        print(f"  ✗ SELECT failed: {e}")
    
    # Test 2: DROP existing view first
    print("\n🧪 Test 2: Drop view if exists, then create...")
    try:
        cur.execute('DROP VIEW IF EXISTS banking.analytics.stg.customers')
        print("  ✓ Dropped view")
    except Exception as e:
        print(f"  ✗ Drop failed: {e}")
    
    # Test 3: Create view without the extra whitespace
    print("\n🧪 Test 3: Create view with clean SQL...")
    sql3 = '''
CREATE OR REPLACE VIEW banking.analytics.stg.customers AS
with ranked as (
    select
        v:id::string            as customer_id,
        v:first_name::string    as first_name,
        v:last_name::string     as last_name,
        v:email::string         as email,
        v:created_at::timestamp as created_at,
        current_timestamp()       as load_timestamp,
        row_number() over (
            partition by v:id::string
            order by v:created_at desc
        ) as rn
    from banking.raw.customers
)

select
    customer_id,
    first_name,
    last_name,
    email,
    created_at,
    load_timestamp
from ranked
where rn = 1
    '''
    try:
        cur.execute(sql3)
        print("  ✓ View created successfully!")
        
        # Verify
        cur.execute('SELECT * FROM banking.analytics.stg.customers LIMIT 1')
        result = cur.fetchone()
        print(f"  ✓ View query works!")
    except Exception as e:
        print(f"  ✗ Create view failed: {e}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Connection error: {e}")
    import traceback
    traceback.print_exc()
