-- Đánh Index trên bảng Fact để tăng tốc độ Dashboard truy vấn 1 triệu giao dịch
CREATE INDEX IF NOT EXISTS idx_fact_tx_account ON warehouse.fact_transactions(account_key);
CREATE INDEX IF NOT EXISTS idx_fact_tx_customer ON warehouse.fact_transactions(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_tx_merchant ON warehouse.fact_transactions(merchant_key);
CREATE INDEX IF NOT EXISTS idx_fact_tx_date ON warehouse.fact_transactions(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_tx_timestamp ON warehouse.fact_transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_fact_loan_customer ON warehouse.fact_loans(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_loan_date ON warehouse.fact_loans(start_date_key);
