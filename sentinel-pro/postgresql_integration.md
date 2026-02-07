# PostgreSQL Integration Guide for Sentinel-Pro

Sentinel-Pro is configured to use SQLite by default for simplicity. Follow these steps to upgrade to a production-grade PostgreSQL database.

## 1. Prerequisites
- **PostgreSQL Server**: Installed and running (local or cloud).
- **Database**: Create a new empty database (e.g., `sentinel_db`).
  ```sql
  CREATE DATABASE sentinel_db;
  ```

## 2. Update Configuration
Modify `backend/core/config.py` to point to your PostgreSQL instance.

```python
# OLD (SQLite)
# DB_PATH = os.path.join(DB_DIR, "sentinel.db")

# NEW (PostgreSQL)
DB_USER = "postgres"
DB_PASS = "password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "sentinel_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```

## 3. Update Sentinel Hub (`core/sentinel_hub.py`)
Replace the raw `sqlite3` driver with `SQLAlchemy` for robust connection pooling and ORM features.

### A. Install Dependencies (Already added to requirements)
```bash
pip install psycopg2-binary sqlalchemy
```

### B. Refactor `_init_db` and `log_alert`
Use `sqlalchemy` engine instead of `sqlite3.connect`.

```python
from sqlalchemy import create_engine, text
from .config import DATABASE_URL

class SentinelHub:
    def __init__(self):
        # ... setup ...
        self.engine = create_engine(DATABASE_URL)
        self._init_db()

    def _init_db(self):
        with self.engine.connect() as conn:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id SERIAL PRIMARY KEY,
                    timestamp FLOAT,
                    risk_level TEXT,
                    details TEXT
                )
            '''))
            conn.commit()

    def log_alert(self, risk: str, details: str):
        with self.engine.connect() as conn:
            conn.execute(text("INSERT INTO alerts (timestamp, risk_level, details) VALUES (:t, :r, :d)"),
                         {"t": time.time(), "r": risk, "d": details})
            conn.commit()
```

## 4. Migration Strategy
If you have existing data in `sentinel.db` (SQLite), dump it using a tool like `pgloader` or a custom Python script before switching over.

```bash
# Example using pgloader
pgloader sqlite:///path/to/sentinel.db postgresql:///sentinel_db
```
