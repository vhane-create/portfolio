-- SQLite 3.25+; simulated monthly FP&A data in USD.
PRAGMA foreign_keys = ON;
BEGIN;
CREATE TABLE categories (
  category_id INTEGER PRIMARY KEY,
  category_name TEXT NOT NULL UNIQUE,
  category_type TEXT NOT NULL CHECK (category_type IN ('Revenue','Expense'))
);
CREATE TABLE budgets (
  month TEXT NOT NULL,
  category_id INTEGER NOT NULL REFERENCES categories(category_id),
  amount REAL NOT NULL CHECK(amount >= 0),
  PRIMARY KEY(month, category_id)
);
CREATE TABLE transactions (
  transaction_id TEXT PRIMARY KEY,
  month TEXT NOT NULL,
  category_id INTEGER NOT NULL REFERENCES categories(category_id),
  amount REAL NOT NULL CHECK(amount >= 0)
);
INSERT INTO categories VALUES
 (1,'Revenue','Revenue'),(2,'Payroll','Expense'),
 (3,'Supplies','Expense'),(4,'Rent','Expense');
INSERT INTO budgets VALUES
 ('2026-10',1,100000),('2026-10',2,40000),
 ('2026-10',3,15000),('2026-10',4,10000);
INSERT INTO transactions VALUES
 ('T001','2026-10',1,55000),('T002','2026-10',1,40000),
 ('T003','2026-10',2,21000),('T004','2026-10',2,22000),
 ('T005','2026-10',3,10000),('T006','2026-10',3,8000),
 ('T007','2026-10',4,10000);
COMMIT;
