import time
import psycopg2
from psycopg2 import sql
from decimal import Decimal, ROUND_DOWN
from faker import Faker
import random
import argparse
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Project configuration
# -----------------------------
NUM_CUSTOMERS = 10
ACCOUNTS_PER_CUSTOMER = 2
NUM_TRANSACTIONS = 50
MAX_TXN_AMOUNT = Decimal("1000.00")
CURRENCY = "USD"

# Non-zero initial balances
INITIAL_BALANCE_MIN = Decimal("10.00")
INITIAL_BALANCE_MAX = Decimal("1000.00")

# Loop config
DEFAULT_LOOP = True
SLEEP_SECONDS = 2

# -----------------------------
# CLI
# -----------------------------
parser = argparse.ArgumentParser(description="Run fake data generator")
parser.add_argument("--once", action="store_true", help="Run a single iteration and exit")
parser.add_argument("--sleep", type=int, default=SLEEP_SECONDS, help="Sleep seconds between iterations (loop mode)")
args = parser.parse_args()

LOOP = (not args.once) and DEFAULT_LOOP
SLEEP_SECONDS = args.sleep

# -----------------------------
# Helpers
# -----------------------------
fake = Faker()

def random_money(min_val: Decimal, max_val: Decimal) -> Decimal:
    """Return a random money amount with 2 decimal places."""
    val = Decimal(str(random.uniform(float(min_val), float(max_val))))
    return val.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

def get_env_or_fail(key: str) -> str:
    """Read required env var or exit with a clear error."""
    v = os.getenv(key)
    if not v:
        print(f"❌ Missing required environment variable: {key}", flush=True)
        sys.exit(1)
    return v

# -----------------------------
# Connect to Postgres (with timeouts)
# -----------------------------
# These prevent the script from "hanging forever" on a bad DB connection or locked query.
conn = psycopg2.connect(
    host=get_env_or_fail("POSTGRES_HOST"),
    port=get_env_or_fail("POSTGRES_PORT"),
    dbname=get_env_or_fail("POSTGRES_DB"),
    user=get_env_or_fail("POSTGRES_USER"),
    password=get_env_or_fail("POSTGRES_PASSWORD"),
    connect_timeout=10,                          # fail fast if DB unreachable
    options="-c statement_timeout=15000",        # 15s query timeout
)
conn.autocommit = True
cur = conn.cursor()

# -----------------------------
# Core generation logic (one iteration)
# -----------------------------
def run_iteration(iteration: int) -> None:
    """
    Generates:
      - NUM_CUSTOMERS customers
      - ACCOUNTS_PER_CUSTOMER accounts per customer
      - NUM_TRANSACTIONS random transactions
    """
    print(f"Iteration {iteration}: Phase 1/3 - customers", flush=True)

    customers = []

    # IMPORTANT FIX:
    # Faker().unique persists across loops. If you loop long enough, it can eventually hang/slow or raise errors.
    # We clear the unique generator each iteration to keep it stable.
    fake.unique.clear()

    for i in range(NUM_CUSTOMERS):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()

        cur.execute(
            "INSERT INTO customers (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id",
            (first_name, last_name, email),
        )
        customer_id = cur.fetchone()[0]
        customers.append(customer_id)

    print(f"Iteration {iteration}: Phase 2/3 - accounts", flush=True)

    accounts = []
    for customer_id in customers:
        for _ in range(ACCOUNTS_PER_CUSTOMER):
            account_type = random.choice(["SAVINGS", "CHECKING"])
            initial_balance = random_money(INITIAL_BALANCE_MIN, INITIAL_BALANCE_MAX)

            cur.execute(
                "INSERT INTO accounts (customer_id, account_type, balance, currency) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                (customer_id, account_type, initial_balance, CURRENCY),
            )
            account_id = cur.fetchone()[0]
            accounts.append(account_id)

    print(f"Iteration {iteration}: Phase 3/3 - transactions", flush=True)

    txn_types = ["DEPOSIT", "WITHDRAWAL", "TRANSFER"]

    for _ in range(NUM_TRANSACTIONS):
        account_id = random.choice(accounts)
        txn_type = random.choice(txn_types)

        # Keep as Decimal for consistency (and better for money)
        amount = random_money(Decimal("1.00"), MAX_TXN_AMOUNT)

        related_account = None
        if txn_type == "TRANSFER" and len(accounts) > 1:
            related_account = random.choice([a for a in accounts if a != account_id])

        cur.execute(
            "INSERT INTO transactions (account_id, txn_type, amount, related_account_id, status) "
            "VALUES (%s, %s, %s, %s, 'COMPLETED')",
            (account_id, txn_type, amount, related_account),
        )

    print(
        f"✅ Iteration {iteration} done: {len(customers)} customers, {len(accounts)} accounts, {NUM_TRANSACTIONS} transactions.",
        flush=True,
    )

# -----------------------------
# Main loop
# -----------------------------
try:
    iteration = 0
    print(f"LOOP={LOOP} (use --once to run one iteration)", flush=True)

    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} started ---", flush=True)

        try:
            run_iteration(iteration)
        except Exception as e:
            # Print the actual error so you can see why it stopped
            print(f"❌ Iteration {iteration} failed: {type(e).__name__}: {e}", flush=True)
            raise  # re-raise so container/runner shows the failure clearly

        print(f"--- Iteration {iteration} finished ---", flush=True)

        if not LOOP:
            break

        time.sleep(SLEEP_SECONDS)

except KeyboardInterrupt:
    print("\nInterrupted by user. Exiting gracefully...", flush=True)

finally:
    try:
        cur.close()
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass
    sys.exit(0)