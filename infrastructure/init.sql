CREATE SCHEMA IF NOT EXISTS tickets_app;

CREATE TABLE IF NOT EXISTS tickets_app.tickets (
    ticket_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    category TEXT NOT NULL DEFAULT 'software',
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tickets_app.ticket_messages (
    message_id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL,
    message_text TEXT NOT NULL,
    author TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_ticket_messages_ticket
        FOREIGN KEY (ticket_id) REFERENCES tickets_app.tickets(ticket_id)
);

CREATE TABLE IF NOT EXISTS tickets_app.cities (
    city_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    state CHAR(2) NOT NULL,
    latitude NUMERIC(7,4),
    longitude NUMERIC(7,4),
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tickets_app.weather_docs (
    weather_id TEXT PRIMARY KEY,
    location TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'forecast',
    headline TEXT,
    narrative_text TEXT NOT NULL,
    event_date TIMESTAMPTZ NOT NULL,
    payload TEXT NOT NULL,
    synced_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

