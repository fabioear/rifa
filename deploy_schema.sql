CREATE TABLE IF NOT EXISTS whatsapp_sessions (
    phone_number VARCHAR PRIMARY KEY,
    step VARCHAR DEFAULT 'MENU',
    temp_data JSON DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='rifas' AND column_name='valor_premio') THEN
        ALTER TABLE rifas ADD COLUMN valor_premio NUMERIC(10, 2);
    END IF;
END $$;
