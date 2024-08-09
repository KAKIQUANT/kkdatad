CREATE TABLE users (
    id UUID DEFAULT generateUUIDv4(),
    username String,
    email String,
    api_key String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (created_at);
