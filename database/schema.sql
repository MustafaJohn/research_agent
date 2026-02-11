-- PostgreSQL schema for appointment chatbot SaaS prototype

CREATE TABLE users (
    id UUID PRIMARY KEY,
    business_id TEXT NOT NULL DEFAULT 'demo-business',
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (business_id, email)
);

CREATE TABLE appointments (
    id UUID PRIMARY KEY,
    business_id TEXT NOT NULL DEFAULT 'demo-business',
    user_id UUID NOT NULL REFERENCES users(id),
    service_name TEXT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    customer_phone TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'confirmed', 'cancelled', 'rescheduled')),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY,
    business_id TEXT NOT NULL DEFAULT 'demo-business',
    user_id UUID NOT NULL REFERENCES users(id),
    appointment_id UUID REFERENCES appointments(id),
    channel TEXT NOT NULL DEFAULT 'web',
    transcript JSONB NOT NULL DEFAULT '[]'::jsonb,
    message_count INT NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);

-- Indexing strategy
CREATE INDEX idx_users_business_email ON users (business_id, email);
CREATE INDEX idx_appointments_business_date_time ON appointments (business_id, appointment_date, appointment_time);
CREATE INDEX idx_appointments_user_status ON appointments (user_id, status);
CREATE INDEX idx_chat_sessions_user_started ON chat_sessions (user_id, started_at DESC);
CREATE INDEX idx_chat_sessions_transcript_gin ON chat_sessions USING GIN (transcript);

-- Sample data
INSERT INTO users (id, business_id, name, email, password_hash)
VALUES
('11111111-1111-1111-1111-111111111111', 'demo-business', 'Demo User', 'demo@example.com', '$2a$10$demoHash');

INSERT INTO appointments (
    id, business_id, user_id, service_name, appointment_date, appointment_time, customer_phone, status, notes
)
VALUES
('22222222-2222-2222-2222-222222222222', 'demo-business', '11111111-1111-1111-1111-111111111111', 'Haircut', '2026-01-03', '11:00', '+1-555-0100', 'confirmed', 'Booked from chatbot');

INSERT INTO chat_sessions (
    id, business_id, user_id, appointment_id, transcript, message_count
)
VALUES
(
    '33333333-3333-3333-3333-333333333333',
    'demo-business',
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    '[{"role":"user","content":"Need haircut tomorrow"},{"role":"assistant","content":"Booked at 11:00"}]'::jsonb,
    2
);
