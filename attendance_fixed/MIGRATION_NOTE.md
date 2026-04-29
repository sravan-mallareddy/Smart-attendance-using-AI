# Database Migration Required

After pulling these changes, you need to add the `laptop_serial` column to your existing database.

## Option A — Fresh start (easiest, if you don't have real data yet)
Just delete `attendance.db` (or whatever your SQLite file is named) and restart the backend.
SQLAlchemy will auto-create all tables with the new column.

## Option B — Migrate existing database
Run this SQL against your database:

```sql
ALTER TABLE employees ADD COLUMN laptop_serial VARCHAR(100);
```

### SQLite (via command line):
```bash
sqlite3 attendance.db "ALTER TABLE employees ADD COLUMN laptop_serial VARCHAR(100);"
```

### After migration, restart the backend:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```
