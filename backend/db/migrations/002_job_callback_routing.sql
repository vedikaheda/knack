ALTER TABLE job_executions
    ADD COLUMN IF NOT EXISTS callback_channel TEXT,
    ADD COLUMN IF NOT EXISTS callback_to TEXT,
    ADD COLUMN IF NOT EXISTS callback_account_id TEXT;
