# 🏦 Banking Modern Data Stack

A production-ready data engineering pipeline for a banking system that demonstrates a modern cloud-native data architecture using open-source and cloud tools.

## 📋 Overview

This project implements a complete data pipeline for a banking system that:
- **Generates** synthetic banking data (customers, accounts, transactions)
- **Captures** real-time changes using CDC (Change Data Capture) via Kafka & Debezium
- **Stores** raw data in MinIO (S3-compatible object storage)
- **Transforms** data using dbt and SQL
- **Loads** data into Snowflake data warehouse
- **Orchestrates** workflows with Apache Airflow

### Use Cases
- Real-time data pipeline for banking operations
- Learning modern data engineering practices
- Demonstrating ELT (Extract, Load, Transform) patterns
- Testing CDC implementations at scale

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Pipeline                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PostgreSQL ──(Debezium)──> Kafka ───> MinIO                    │
│      ↑                                      ↓                     │
│  Faker Generator                        dbt Transformations      │
│  (Generates fake data)                      ↓                     │
│                                        Snowflake Analytics       │
│                                            ↓                     │
│                                      Airflow Orchestration       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Source** | PostgreSQL 15 | Transactional database |
| **CDC** | Debezium 2.2 | Captures database changes |
| **Message Queue** | Kafka 7.4 | Streams data changes |
| **Data Lake** | MinIO | S3-compatible object storage |
| **Data Warehouse** | Snowflake | Cloud analytics platform |
| **Transformation** | dbt | Data transformations & testing |
| **Orchestration** | Apache Airflow | Workflow management |
| **Language** | Python 3.13 | Script development |

---

## 📦 Prerequisites

### Required
- Docker & Docker Compose
- Python 3.10+
- Snowflake account
- Git

### Optional
- dbt CLI (installed via pip)
- Snowflake CLI

---

## 📁 Project Structure

```
banking-modern-stack/
├── banking_dbt/                    # dbt project for transformations
│   ├── models/
│   │   ├── staging/               # Staging views (raw → clean)
│   │   │   ├── stg_customers.sql  # Customer transformation
│   │   │   ├── stg_accounts.sql   # Account transformation
│   │   │   └── stg_transactions.sql # Transaction transformation
│   │   ├── marts/                 # Business models (analytics)
│   │   └── sources.yml            # Data source definitions
│   ├── dbt_project.yml            # dbt configuration
│   └── target/                    # Compiled SQL (generated)
│
├── data-generator/                 # Synthetic data generation
│   └── faker_generator.py          # Generates fake banks data
│
├── consumer/                        # Kafka consumers
│   └── kafka_to_minio.py          # Consumes Kafka → MinIO
│
├── kafka-debezium/                 # CDC configuration
│   └── generate_and_post_connecter.py # Sets up Debezium connectors
│
├── docker/                          # Docker services
│   ├── dags/                       # Airflow DAGs
│   │   └── minio_to_snowflake_dag.py # Airflow orchestration
│   ├── logs/                       # Service logs
│   ├── postgres/                   # PostgreSQL data
│   └── minio/                      # MinIO data
│
├── docker-compose.yml              # Multi-container setup
├── dockerfile-airflow.dockerfile   # Airflow image
├── requirements.txt                # Python dependencies
└── setup_raw_tables.sql            # Snowflake table initialization
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone repository
git clone <repo-url>
cd banking-modern-stack

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=banking_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_PASSWORD=docker

# Kafka
KAFKA_BOOTSTRAP=kafka:9092
KAFKA_GROUP=banking-consumer

# MinIO
MINIO_ENDPOINT=http://localhost:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=banking-data
MINIO_LOCAL_DIR=/tmp/minio_downloads

# Snowflake
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account.region.cloud
SNOWFLAKE_WAREHOUSE=compute_wh
SNOWFLAKE_DB=banking
SNOWFLAKE_SCHEMA=raw

# Airflow
AIRFLOW_DB_USER=airflow
AIRFLOW_DB_PASSWORD=airflow
AIRFLOW_DB_NAME=airflow_db
```

### 3. Start Docker Services

```bash
# Start all services (PostgreSQL, Kafka, MinIO, Airflow, etc.)
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Initialize Snowflake

```bash
# Create raw schema and tables in Snowflake
python create_raw_tables.py
```

### 5. Setup Debezium CDC

Open a new terminal and run:

```bash
# Configure Debezium connectors to capture PostgreSQL changes
python kafka-debezium/generate_and_post_connecter.py
```

### 6. Generate Data

Open a new terminal and run:

```bash
# Generate fake banking data once
python data-generator/faker_generator.py --once

# Or continuously generate data every 2 seconds
python data-generator/faker_generator.py --sleep 2
```

### 7. Consume & Load Data

Open a new terminal and run:

```bash
# Start Kafka consumer (sends data to MinIO)
python consumer/kafka_to_minio.py
```

### 8. Transform with dbt

```bash
cd banking_dbt

# Verify connection to Snowflake
dbt debug

# Run dbt transformations
dbt run

# Run tests
dbt test
```

### 9. Access Airflow

Open browser: `http://localhost:8080`

- Username: `airflow`
- Password: `airflow`

---

## 📊 Data Flow

### Step-by-Step Process

1. **Data Generation** (faker_generator.py)
   - Generates 10 customers with 2 accounts each
   - Creates 50 transactions per iteration
   - Inserts into PostgreSQL every 2 seconds

2. **Change Capture** (Debezium)
   - Detects INSERT/UPDATE/DELETE on customers, accounts, transactions
   - Publishes CDC events to Kafka topics:
     - `banking_server.public.customers`
     - `banking_server.public.accounts`
     - `banking_server.public.transactions`

3. **Data Streaming** (Kafka)
   - Maintains topics in Kafka brokers
   - Available for real-time consumption

4. **Storage** (MinIO)
   - Consumer batches 50 messages and exports to Parquet
   - Organizes by table and date:
     - `s3://banking-data/customers/date=2026-02-23/`
     - `s3://banking-data/accounts/date=2026-02-23/`
     - `s3://banking-data/transactions/date=2026-02-23/`

5. **Loading** (Airflow)
   - Downloads Parquet files from MinIO
   - Loads into Snowflake `RAW` schema
   - Runs on schedule (every minute)

6. **Transformation** (dbt)
   - Cleans and transforms raw data
   - Creates staging views:
     - `BANKING.ANALYTICS.STG_CUSTOMERS`
     - `BANKING.ANALYTICS.STG_ACCOUNTS`
     - `BANKING.ANALYTICS.STG_TRANSACTIONS`
   - Creates business models for analysis

---

## 📝 Key Files

### Data Generation
- **`data-generator/faker_generator.py`**: Generates synthetic banking data
  - Customers with emails and names
  - Accounts with balances and types
  - Transactions between accounts
  - Default: 10 customers, 2 accounts each, 50 transactions per run

### CDC & Streaming
- **`kafka-debezium/generate_and_post_connecter.py`**: Configures Debezium
  - Sets up PostgreSQL source connector
  - Maps to Kafka topics
  - Enables logical decoding replication

### Data Loading
- **`consumer/kafka_to_minio.py`**: Kafka → MinIO consumer
  - Batches 50 messages per write
  - Converts to Parquet format
  - Partitions by table and date

### Transformations
- **`banking_dbt/models/staging/*`**: Staging layer
  - Deduplicates records (uses ROW_NUMBER)
  - Casts types and normalizes fields
  - Handles late-arriving data

### Orchestration
- **`docker/dags/minio_to_snowflake_dag.py`**: Airflow DAG
  - Downloads files from MinIO
  - Loads to Snowflake via COPY INTO
  - Runs every minute

---

## 🐛 Troubleshooting

### Issue: "Object does not exist" in dbt
**Solution**: Ensure raw tables are created in Snowflake
```bash
python create_raw_tables.py
```

### Issue: Kafka consumer shows no messages
**Solution**: Ensure data generator and Debezium are running
```bash
# Terminal 1: Data generator
python data-generator/faker_generator.py

# Terminal 2: Kafka consumer
python consumer/kafka_to_minio.py
```

### Issue: Airflow DAG not triggering
**Solution**: Check Airflow logs and verify MinIO connectivity
```bash
docker-compose logs airflow-scheduler
```

### Issue: Snowflake connection fails
**Solution**: Verify credentials in `.env` and test connection
```bash
python create_raw_tables.py  # Tests connection
```

### Issue: dbt models fail to run
**Solution**: Clear cache and check Snowflake permissions
```bash
cd banking_dbt
dbt clean
dbt debug
dbt run
```

---

## 📈 Monitoring

### Check Docker Services
```bash
docker-compose ps
docker-compose logs -f <service-name>
```

### Monitor Data Flow
```bash
# PostgreSQL
docker exec -it postgres psql -U postgres -d banking_db -c "SELECT COUNT(*) FROM customers;"

# MinIO (Web UI)
http://localhost:9001  # minioadmin / minioadmin

# Kafka Topics
docker exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092

# Snowflake
SELECT COUNT(*) FROM BANKING.RAW.customers;
```

---

## 🔧 Configuration

### Adjust Data Generation
Edit `data-generator/faker_generator.py`:
```python
NUM_CUSTOMERS = 100        # Increase customers
ACCOUNTS_PER_CUSTOMER = 5  # More accounts per customer
NUM_TRANSACTIONS = 200     # More transactions
SLEEP_SECONDS = 5          # Slower generation
```

### Adjust Batch Size
Edit `consumer/kafka_to_minio.py`:
```python
batch_size = 100  # Increase batch size for higher throughput
```

### Change Transformation Logic
Edit `banking_dbt/models/staging/stg_*.sql`:
- Add business logic
- Create new dimensions
- Add aggregations

---

## 📚 Learning Resources

### Key Concepts
- **CDC (Change Data Capture)**: Capture database changes in real-time
- **ELT (Extract, Load, Transform)**: Modern approach vs ETL
- **Data Warehouse**: Snowflake for analytics
- **Data Transformations**: dbt for SQL-first development
- **Orchestration**: Airflow for workflow management

### Useful Links
- [dbt Documentation](https://docs.getdbt.com/)
- [Debezium](https://debezium.io/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Snowflake](https://docs.snowflake.com/)
- [Apache Airflow](https://airflow.apache.org/)

---

## 🤝 Contributing

To extend this project:
1. Add new data sources or entities
2. Create additional dbt models and tests
3. Add new Airflow DAGs for specific workflows
4. Implement data quality checks
5. Add documentation for new features

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🎯 Next Steps

### To Deploy to Production
- [ ] Replace Kafka with managed service (AWS MSK, Confluent Cloud)
- [ ] Replace MinIO with S3
- [ ] Scale PostgreSQL → RDS or managed database
- [ ] Containerize all Python scripts
- [ ] Set up CI/CD pipeline
- [ ] Add data quality tests & Great Expectations
- [ ] Implement data lineage tracking (OpenLineage)
- [ ] Add monitoring & alerting (Datadog, Prometheus)

### To Enhance the Project
- [ ] Add customer segmentation models
- [ ] Create financial analytics marts
- [ ] Build anomaly detection for fraudulent transactions
- [ ] Add dimensional models (star schema)
- [ ] Implement slowly changing dimensions (SCD)

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the logs: `docker-compose logs <service>`
3. Test individual components in isolation
4. Verify `.env` configuration

---

**Last Updated**: February 23, 2026  
**Version**: 1.0.0
